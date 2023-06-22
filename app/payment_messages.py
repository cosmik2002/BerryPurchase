import datetime
import io
import os
import re
import sys
import traceback
from collections import namedtuple
from typing import List

from flask import current_app
from pandas import DataFrame
from sqlalchemy import or_, func
from sqlalchemy.orm import Query
from tqdm import tqdm
from app.pdf_read import ReadSberStatementPdf
from database import SessionRemote, Session
from app.models import smsMsg, Payments, Payers, PaymentsSchema
from datetime import datetime as dt

PayerData = namedtuple('PayerData', 'name card_number text bank_name')


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class PaymentsProcessor:

    def __init__(self):
        self.session = Session()
        self.counters = None
        self.banks = ['TINKOFF BANK', 'Tinkoff', 'Тинькофф Банк', 'Альфа Банк', 'ВТБ']

    def parse_sms(self, msg, rec_date):
        if msg.find('MIR2462') != -1 or msg.find('МИР2462') != -1:
            find = False
            patterns = (
                r'MIR2462 (?P<date>\d{2}.\d{2}.\d{2}) зачислен перевод (?P<summ>[\d\s,]+)[р|\u20bd] из (?P<bank>\w+[ \w]*) от (?P<sender>\w+ \w+ \w+)',
                r'MIR2462 (?P<time>\d{2}:\d{2}) (?P<sender>\w+ \w+)\. перевел\(а\) вам (?P<summ>[\d\s,]+)[р|\u20bd]\.~Зачисление из (?P<bank>\w+[ \w]*)',
                r'МИР2462 (?P<time>\d{2}:\d{2}) (?P<sender>\w+ \w+)\. перевел\(а\) вам (?P<summ>[\d\s,]+)[р|\u20bd]\.~Зачисление из (?P<bank>\w+[ \w]*)',
                r'МИР2462 (?P<time>\d{2}:\d{2}) (?P<sender>\w+ \w+)\. перевел\(а\) вам (?P<summ>[\d\s,]+)[р|\u20bd]\.',
                r'MIR2462 (?P<time>\d{2}:\d{2}) Перевод (?P<summ>[\d\s,]+)[р|\u20bd] от (?P<sender>\w+ \w+)\.',
                r'MIR2462 (?P<time>\d{2}:\d{2}) Перевод (?P<summ>[\d\s,]+)[р|\u20bd] от (?P<sender>\w+ \w+ \w+)\.',
                r'(?P<summ>[\d\s,]+)[р|\u20bd] MIR2462~Перевод от (?P<sender>\w+ \w+ \w+)\.',
                r'\[(?P<date>\d{2}.\d{2}.\d{4}) в (?P<time>\d{2}:\d{2})\]\nЗачислен перевод\nMIR2462 (\d{2}.\d{2}.\d{2}) зачислен перевод (?P<summ>[\d\s,]+)[р|\u20bd] из (?P<bank>\w+[ \w]*) от (?P<sender>\w+ \w+ \w+)',
                r'\[(?P<date>\d{2}.\d{2}.\d{4}) в (?P<time>\d{2}:\d{2})\]\nЗачисление из (?P<bank>\w+[ \w]*)\nМИР2462 (\d{2}:\d{2}) (?P<sender>\w+ \w+)\. перевел\(а\) вам (?P<summ>[\d\s,]+)[р|\u20bd]\.'
            )
            for pattern in patterns:
                m = re.match(pattern, msg)
                if m:
                    gr = m.groupdict()
                    print(gr.get('date'), gr.get('time'), gr['summ'], gr.get('bank'), gr['sender'])
                    date = rec_date
                    if gr.get('date') and gr.get('time'):
                        date = dt.strptime(f"{gr['date']} {gr['time']}", "%d.%m.%Y %H:%M")
                    elif gr.get('time'):
                        date = rec_date.replace(hour=int(gr['time'][:2]), minute=int(gr['time'][3:]), second=0)
                    else:
                        date = rec_date
                    find = True
                    summ = gr['summ'].replace(',', '.')
                    return gr['sender'], summ, date, gr.get('bank')
            if not find:
                self.log(f"missed regex {msg}")
                return None, None, None, None
        return None, None, None, None

    def get_payments(self, session, page, page_size, search_options):
        query: Query = session.query(Payments)

        src = search_options['src']

        if search_options['start_date']:
            start_date = dt.strptime(search_options['start_date'], '%Y/%m/%d')
            query = query.filter(Payments.timestamp >= start_date)
        if src:
            query = query.join(Payers, isouter=True)
            query = query.filter(or_(Payers.card_number.like(f"%{src}%"), Payments.comment.like(f"%{src}%"),
                                     Payments.sum == src if is_number(src) else False))
        query = query.order_by(Payments.timestamp.desc())
        if page_size:
            query = query.limit(page_size)
            if page:
                query = query.offset((page - 1) * page_size)
        payments = query.all()
        payments_schema = PaymentsSchema(many=True, exclude=('payer',))
        output = payments_schema.dumps(payments)
        return output

    def find_and_update_payer(self, payer_data: PayerData, multi_payers=False):
        def check_payers(payers):
            if len(payers) > 1:
                if multi_payers:
                    return payers
                self.log(f"Too many payers {payer_data.name} {payer_data.card_number} {payer_data.text}")
                return False
            payer = payers[0]
            if not payer.card_number and payer_data.card_number:
                payer.card_number = payer_data.card_number
            if not payer.bank_name and payer_data.bank_name:
                payer.bank_name = payer_data.bank_name
            if len(payer.name.split()) < 3 and len(payer_data.name.split()) == 3:
                payer.name = payer_data.name
            self.session.commit()
            return [payer]

        if payer_data.card_number:
            payer = self.session.query(Payers).filter_by(card_number=payer_data.card_number).all()
            if payer:
                return check_payers(payer)
        if payer_data.name:
            payer = self.session.query(Payers).filter_by(name=payer_data.name).all()
            if payer:
                return check_payers(payer)

        # если плетельщик из двух слов, пытаемся найти по имени и букве фамилии
        if len(sender_parts := payer_data.name.split()) == 2:
            payer = self.session.query(Payers).filter(Payers.name.like(f"{sender_parts[0]} % {sender_parts[1]}")).all()
            if payer:
                return check_payers(payer)

        # если плетельщик из трех слов, пытаемся найти по имени и букве фамилии
        if payer_data.name != '' and len(payers_parts := payer_data.name.split()) == 3:
            payer = self.session.query(Payers).filter(Payers.name == f"{payers_parts[0]} {payers_parts[2]}").all()
            if payer:
                return check_payers(payer)

        if payer_data.name != '' or payer_data.card_number != '':
            payer = Payers(name=payer_data.name.upper(), card_number=payer_data.card_number, comments=payer_data.text)
            self.session.add(payer)
            self.session.commit()
            self.counters['payers_add'] += 1
            return [payer]

    def find_and_update_payment(self):
        pass

    def parse_sber_statement(self, file):
        result: DataFrame = ReadSberStatementPdf().read_and_parse_doc(file)
        self.counters = {
            'payers_add': 0,
            'payments_update': 0,
            'payments_add': 0,
            'errors': []
        }
        op_codes = {}
        for row in tqdm(result.itertuples()):
            payment = self.session.query(Payments).filter(Payments.operation_code == row.code,
                                                          Payments.timestamp.between(row.date,
                                                                                     row.date + datetime.timedelta(
                                                                                         days=1))).all()
            # костыль для комиссий сбера которые идут с тем-же кодом операции
            if row.code in op_codes:
                op_codes[row.code] += float(row.summa)
                if payment[0].sum != op_codes[row.code]:
                    self.log(f"sum updated {row.code} {payment[0].sum} -> {op_codes[row.code]}")
                    print(row.code, row.summa)
                    payment[0].sum = op_codes[row.code]
                    self.session.commit()
            else:
                op_codes[row.code] = float(row.summa)
            if payment:
                continue
            bank = ''
            for bank_tag in self.banks:
                if bank_tag in row.name:
                    bank = bank_tag
                    break

            payer = self.find_and_update_payer(
                PayerData(card_number=row.card_number, name=row.payer.upper(), text=row.name, bank_name=bank))
            payer = payer[0] if payer else payer
            # if not payer:
            # self.log(f"payment skiped {row}")
            # continue
            start_date = row.date - datetime.timedelta(
                minutes=90)  # notify may be earler then operations due start transaction
            end_date = row.date + datetime.timedelta(minutes=15)
            payment: List[Payments] = self.session.query(Payments).filter(Payments.sum == row.summa,
                                                                          Payments.operation_code == None,
                                                                          Payments.timestamp.between(start_date,
                                                                                                     end_date)).all()
            if payment:
                if len(payment) > 1:
                    if isinstance(payer, Payers):
                        payment = list(
                            filter(lambda p: p.payer == None or p.payer.id == payer.id,
                                   payment))
                    if len(payment) > 1:
                        self.log(
                            "too many payments " + ';'.join([f"{p.id} {p.timestamp} {p.comment}" for p in payment]))
                        continue
                payment[0].operation_code = row.code
                if payer and payer.card_number:
                    payment[0].payer_id = payer.id
                if row.name not in payment[0].comment:
                    payment[0].comment = payment[0].comment + ";" + row.name
                self.session.commit()
                self.counters['payments_update'] += 1
            else:
                self.session.add(
                    Payments(operation_code=row.code, payer_id=payer.id if payer else None, timestamp=row.date,
                             sum=row.summa,
                             date_processed=row.date1, comment=row.name))
                self.session.commit()
                self.counters['payments_add'] += 1
        return self.counters

    def parse_and_save_payment(self, id, text, date):
        payment = self.session.query(Payments).filter_by(sms_id=id).all()
        if not payment:
            (sender, summa, sms_date, bank) = self.parse_sms(text, date)
            date = sms_date or date
            if sender:
                sender = sender.upper()
                payer = self.find_and_update_payer(PayerData(name=sender, card_number=None, text=text, bank_name=bank),
                                                   multi_payers=True
                                                   )
                if not payer:
                    self.log(f"payment skiped {id} {text} {date}")
                    return
                start_date = date - datetime.timedelta(minutes=30)
                end_date = date + datetime.timedelta(minutes=90)
                payment: List[Payments] = self.session.query(Payments).filter(Payments.sum == summa,
                                                                              Payments.timestamp.between(start_date,
                                                                                                         end_date)).all()
                if payment:
                    if len(payment) > 1:
                        # пробуем найти нужный платеж
                        if isinstance(payer, List):
                            ids = [p.id for p in payer]
                            payment = list(filter(
                                lambda p: p.payer == None or p.payer.id in ids or bank and bank in p.comment,
                                payment))
                        else:
                            payment = list(filter(
                                lambda p: p.payer == None or p.payer.id == payer.id or bank and bank in p.comment,
                                payment))
                    if len(payment) > 1:
                        self.log("too many payments " + ';'.join([f"{p.id} {p.comment}" for p in payment]))
                        return
                    if not payment:
                        self.log(f'payment not selected {id} {text}')
                        return
                    self.counters['payments_update'] += 1
                    if not payment[0].sms_id:
                        payment[0].sms_id = id
                    if payer and payer[0].name and payment[0].payer_id is None:
                        payment[0].payer_id = payer[0].id
                    if text not in payment[0].comment:
                        payment[0].comment = payment[0].comment + ";" + text
                    self.session.commit()
                else:
                    if len(payer) == 1:
                        payer = payer[0]
                        self.session.add(
                            Payments(sms_id=id, payer_id=payer.id, timestamp=date, sum=summa, comment=text))
                        self.session.commit()
                        self.counters['payments_add'] += 1
                    else:
                        self.log(f"payment skiped (no payment/multipayer) {id} {text} {date}")

    def log(self, msg, level='info'):
        self.counters['errors'].append(msg)
        if level == 'info':
            current_app.logger.info(msg)
        else:
            current_app.logger.error(msg)

    def get_payment_messages(self):
        session_remote = SessionRemote()
        start_date = datetime.datetime(2023, 1, 1)
        self.counters = {
            'payers_add': 0,
            'payments_update': 0,
            'payments_add': 0,
            'errors': []
        }
        records: List[smsMsg] = session_remote.query(smsMsg).filter(smsMsg.date > start_date).all()
        for record in records:
            try:
                if record.msg.lstrip().startswith('[') and record.msg.lower().find('\n\n') != -1:
                    for idx, msg in enumerate(record.msg.split('\n\n')):
                        id = (record.id * 100 + idx) * -1
                        self.parse_and_save_payment(id, msg, record.date)
                else:
                    self.parse_and_save_payment(record.id, record.msg, record.date)
            except Exception as ex:
                exc_type, value, tb = sys.exc_info()
                output = io.StringIO()
                traceback.print_tb(tb, file=output)
                s = output.getvalue()
                output.close()
                self.counters['errors'].append(s)

        return self.counters


if __name__ == "__main__":
    PaymentsProcessor().get_payment_messages()
    PaymentsProcessor().parse_sber_statement(r'../Документ-2023-02-06-071313.pdf')
