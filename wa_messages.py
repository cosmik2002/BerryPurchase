import json
from datetime import datetime

import PySimpleGUI as sg

from models import Customers, Messages


def get_wa_messages(session):
    # file = sg.popup_get_file("select File")
    file = r"meggages.json"
    with open(file, encoding='utf-8') as f:
        messages = json.load(f)

    for i, message in enumerate(messages):
        sg.one_line_progress_meter('This is my progress meter!', i, len(messages), '-key-')
        t = datetime.utcfromtimestamp(message['t'])
        sender = message['sender']
        cust = session.query(Customers).filter_by(wa_id=sender['id']).all()
        if not cust:
            cust = Customers(wa_id=sender['id'], name=sender.get('name'), number=sender['formattedName'],
                             short_name=sender.get('shortName'), push_name=sender.get('pushname'))
            session.add(cust)
            session.commit()
        else:
            cust = cust[0]
        msg = session.query(Messages).filter_by(wa_id=message['id']).all()
        if not msg:
            msg = Messages(wa_id=message['id'], customer_id=cust.id, timestamp=t, text=message.get('content'))
            session.add(msg)
            session.commit()

