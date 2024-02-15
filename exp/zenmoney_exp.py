from zenmoney import *
import os
from dotenv import load_dotenv
import datetime

load_dotenv()
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
key = os.getenv('ZENMONEY_KEY')
if not key:
    exit(0)
api = Request(key)
diff: Diff = api.diff(Diff(**{'serverTimestamp': yesterday.timestamp(), 'forceFetch': ['tag', 'account', 'merchant']}))
account: Account = next(filter(lambda a: a.title == 'MIR', diff.account))
tra: Transaction
for tra in diff.transaction:
    if tra.incomeAccount == account.id and tra.income>0:
        tag:Tag = next(filter(lambda t: t.id==tra.tag[0], diff.tag)) if tra.tag else None
        sum = tra.income
        p = tra.originalPayee or tra.payee
        print(tag.title if tag else '', sum, p)
print(diff)
