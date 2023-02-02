import g_sheets
from database import Session
from models import Goods, Messages
from payment_messages import get_payment_messages
from wa_messages import get_wa_messages

session = Session()


# g_sheets.gSheets(session).get_clients()
#
# get_wa_messages(session)
#
# get_payment_messages(session)

def get_message_orders():
    goods = session.query(Goods).all()
    messages = session.query(Messages).all()
    for message in messages:
        found = []
        for good in goods:
            if message.text and any(word in message.text.lower() for word in good.variants.split(';')):
                found.append(good.name)
        if found:
            print(message.text, found)

get_message_orders()