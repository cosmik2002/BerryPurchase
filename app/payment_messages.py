import datetime
import re
from collections import namedtuple
from typing import List

from pandas import DataFrame
from sqlalchemy import or_
from tqdm import tqdm
from app.pdf_read import ReadSberStatementPdf
from database import SessionRemote, Session
from app.models import smsMsg, Payments, Payers, PaymentsSchema
import datetime as dt

PayerData = namedtuple('PayerData', 'name card_number text')


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
        self.banks = ['TINKOFF BANK', 'Tinkoff', 'Тинькофф Банк', 'Альфа Банк', ' ВТБ']

    def parse_sms(self, msg):
        date: datetime = None
        msg = msg.lstrip()
        if msg.startswith('[') and (
                src := re.search('(\d{2}.\d{2}.\d{4}) в (\d{2}:\d{2})', msg[1:19])) is not None:
            date = dt.datetime.strptime(f"{src.group(1)} {src.group(2)}", "%d.%m.%Y %H:%M")
        pos = msg.lower().find('перевод')
        sender = ''
        value = 0
        bank = ''
        for bank_tag in self.banks:
            if bank_tag in msg:
                bank = bank_tag
                break
        if pos != -1:
            # до точки или трильды
            m = re.search(r'от ([^~.]*)', msg)
            if m is not None:
                sender = m.group(1).replace('\xa0', ' ').strip()
            # сумма р
            p = re.compile(r'([\d\s]+)[р|\u20bd]')
            m = re.search(p, msg)
            if m is not None:
                txt = m.group(1)
                value = re.sub(r'\s', '', txt)
                value = value.replace(' ', '')
        elif pos := msg.lower().find('перевел(а) вам') != -1:
            m = re.search(r'([А-Я \xa0]+). перевел\(а\) вам', msg)
            if m is not None:
                sender = m.group(1).replace('\xa0', ' ').strip()

            p = re.compile(r'([\d\s]+)[р\u20bd]')
            m = re.search(p, msg)
            if m is not None:
                txt = m.group(1)
                value = re.sub(r'\s', '', txt)
                value = value.replace(' ', '')

        return sender, value, date, bank

    def get_payments(self, session, page, page_size, src):
        query = session.query(Payments)
        if src:
            query = query.join(Payers, isouter=True)
            query = query.filter(or_(Payers.card_number.like(f"%{src}%"), Payments.comment.like(f"%{src}%"),
                             Payments.sum == src if is_number(src) else False))
        if page_size:
            query = query.limit(page_size)
            if page:
                query = query.offset((page-1) * page_size)
        payments = query.all()
        payments_schema = PaymentsSchema(many=True)
        output = payments_schema.dump(payments)
        return output

    def find_and_update_payer(self, payer_data: PayerData):
        def check_payers(payers):
            if len(payers) > 1:
                raise Exception(f"Too many payers {payer_data.name} {payer_data.card_number} {payer_data.text}")
            payer = payers[0]
            if not payer.card_number and payer_data.card_number:
                payer.card_number = payer_data.card_number
            if len(payer.name.split()) < 3 and len(payer_data.name.split()) == 3:
                payer.name = payer_data.name
            self.session.commit()
            return payer

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
            return payer

    def find_and_update_payment(self):
        pass

    def parse_sber_statement(self, file):
        result: DataFrame = ReadSberStatementPdf().read_and_parse_doc(file)
        self.counters = {
            'payers_add': 0,
            'payments_update': 0,
            'payments_add': 0
        }
        for row in tqdm(result.itertuples()):
            payment = self.session.query(Payments).filter_by(operation_code=row.code).all()
            if payment:
                continue
            payer = self.find_and_update_payer(
                PayerData(card_number=row.card_number, name=row.payer.upper(), text=row.name))
            start_date = row.date - datetime.timedelta(minutes=30)
            end_date = row.date + datetime.timedelta(minutes=30)
            payment: List[Payments] = self.session.query(Payments).filter(Payments.sum == row.summa,
                                                                          Payments.operation_code == None,
                                                                          Payments.timestamp.between(start_date,
                                                                                                     end_date)).all()
            if payment:
                if len(payment) > 1:
                    raise Exception("too many payments " + ';'.join([p.comment for p in payment]))
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
            (sender, summa, sms_date, bank) = self.parse_sms(text)
            date = sms_date or date
            sender = sender.upper()
            if sender:
                payer = self.find_and_update_payer(PayerData(name=sender, card_number=None, text=text))

                start_date = date - datetime.timedelta(minutes=30)
                end_date = date + datetime.timedelta(minutes=30)
                payment: List[Payments] = self.session.query(Payments).filter(Payments.sum == summa,
                                                                              Payments.timestamp.between(start_date,
                                                                                                         end_date)).all()
                if payment:
                    if len(payment) > 1:
                        # пробуем найти нужный платеж
                        payment = list(filter(lambda p: p.payer == None or bank and bank in p.comment, payment))
                    if len(payment) > 1:
                        raise Exception("too many payments " + ';'.join([p.comment for p in payment]))
                    self.counters['payments_update'] += 1
                    if not payment[0].sms_id:
                        payment[0].sms_id = id
                    if payer.name:
                        payment[0].payer_id = payer.id
                    if text not in payment[0].comment:
                        payment[0].comment = payment[0].comment + ";" + text
                    self.session.commit()
                else:
                    self.session.add(
                        Payments(sms_id=id, payer_id=payer.id, timestamp=date, sum=summa, comment=text))
                    self.session.commit()
                    self.counters['payments_add'] += 1

    def get_payment_messages(self):
        session_remote = SessionRemote()
        start_date = datetime.datetime(2023, 1, 1)
        self.counters = {
            'payers_add': 0,
            'payments_update': 0,
            'payments_add': 0
        }
        records: List[smsMsg] = session_remote.query(smsMsg).filter(smsMsg.date > start_date).all()
        for record in records:
            if record.msg.lstrip().startswith('[') and record.msg.lower().find('\n\n') != -1:
                for idx, msg in enumerate(record.msg.split('\n\n')):
                    id = (record.id * 100 + idx) * -1
                    self.parse_and_save_payment(id, msg, record.date)
            else:
                self.parse_and_save_payment(record.id, record.msg, record.date)
        return self.counters


if __name__ == "__main__":
    PaymentsProcessor().get_payment_messages()
    PaymentsProcessor().parse_sber_statement(r'../Документ-2023-02-06-071313.pdf')
