from sqlalchemy.orm import scoped_session, Session
from zenmoney import *
import os
import datetime

from app.models import Payers, Payments
from database import SessionLocal


class ZenMoney:
    def __init__(self, session):
        self.counters = None
        self.session: Session = session
        self.key = os.getenv('ZENMONEY_KEY')
        self.account_title = 'MIR'

    def get_payer(self, tra: Transaction):
        payer_name = (tra.originalPayee or tra.payee or tra.comment).upper()
        payer_name = payer_name.replace(".", '')
        payers = self.session.query(Payers).filter(Payers.name == payer_name).all()
        if payers:
            return payers[0]
        payer = Payers(name=payer_name)
        self.session.add(payer)
        self.session.commit()
        self.counters['payers_add'] +=1
        return payer


    def get_transaction(self, from_date: datetime):
        self.counters = {
            'payers_add': 0,
            'payments_update': 0,
            'payments_add': 0,
            'errors': []
        }
        if not self.key:
            exit(0)
        api = Request(self.key)
        diff: Diff = api.diff(
            Diff(**{'serverTimestamp': from_date.timestamp(), 'forceFetch': ['tag', 'account', 'merchant']}))
        account: Account = next(filter(lambda a: a.title == self.account_title, diff.account))
        tra: Transaction
        for tra in diff.transaction:
            if tra.incomeAccount == account.id and tra.income > 0:
                is_payment = self.session.query(Payments).filter(Payments.operation_code==tra.id).all()
                if is_payment:
                    continue
                tag: Tag = next(filter(lambda t: t.id == tra.tag[0], diff.tag)) if tra.tag else None
                payer = self.get_payer(tra)
                tra_date = datetime.datetime.strptime(tra.date, "%Y-%m-%d")
                self.session.add(Payments(payer_id=payer.id, operation_code=tra.id, sum=tra.income, timestamp=tra_date, comment=tra.comment))
                self.session.commit()
                self.counters['payments_add'] +=1
        return self.counters


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    from_date: datetime = datetime.datetime.now() - datetime.timedelta(days=5)
    ZenMoney(SessionLocal).get_transaction(from_date)
