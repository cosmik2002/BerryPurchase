import re

from app.pdf_read import ReadSberStatementPdf
from database import SessionRemote
from app.models import smsMsg, Payments, Payers


def parse_sms(msg):
    pos = msg.lower().find('перевод')
    sender = ''
    value = 0
    if pos != -1:
        m = re.search('от ([^~.]*)', msg)
        if m is not None:
            sender = m.group(1).replace('\xa0', ' ')
        p = re.compile('([\d\s]+)(р|\u20bd)')
        m = re.search(p, msg)
        if m is not None:
            txt = m.group(1)
            value = re.sub('\s', '', txt)
            value = value.replace(' ', '')
    return sender, value

def parse_sber_statement(file):
    result = ReadSberStatementPdf().read_and_parse_doc(file)

def get_payment_messages(session):
    session_remote = SessionRemote()
    msg = session_remote.query(smsMsg).limit(100).all()
    for q in msg:
        payment = session.query(Payments).filter_by(sms_id=q.id).all()
        if not payment:
            (sender, summa) = parse_sms(q.msg)
            if sender:
                payer = session.query(Payers).filter_by(name=sender).all()
                if not payer:
                    payer = Payers(name=sender, comments=q.msg)
                    session.add(payer)
                    session.commit()
                else:
                    payer = payer[0]
                session.add(Payments(sms_id=q.id, payer_id=payer.id, timestamp=q.date, sum=summa))
                session.commit()
