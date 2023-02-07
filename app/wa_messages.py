import json
from datetime import datetime

import PySimpleGUI as sg

from app.models import Customers, Messages, Goods, MessagesSchema, Clients, ClientsSchema, ClientsLinks, \
    ClientsLinksSchema, CustomersSchema, Payers, PayersSchema


def get_messages(session):
    messages = session.query(Messages).all()
    messages_schema = MessagesSchema(many=True)
    output = messages_schema.dump(messages)
    return output

def get_clients(session):
    clients = session.query(Clients).all()
    clients_schema = ClientsSchema(many=True)
    output = clients_schema.dump(clients)
    return output

def get_customers(session):
    customers = session.query(Customers).all()
    customers_schema = CustomersSchema(many=True)
    output = customers_schema.dump(customers)
    return output

def get_payers(session):
    payers = session.query(Payers).all()
    payers_schema = PayersSchema(many=True)
    output = payers_schema.dump(payers)
    return output

def get_clients_links(session):
    clients_links = session.query(ClientsLinks).all()
    clients_links_schema = ClientsLinksSchema(many=True)
    output = clients_links_schema.dump(clients_links)
    return output

def get_wa_messages(session):
    # file = sg.popup_get_file("select File")
    file = r"../meggages.json"
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


def get_message_orders(session):
    goods = session.query(Goods).all()
    messages = session.query(Messages).all()
    for message in messages:
        found = []
        for good in goods:
            if message.text and any(word in message.text.lower() for word in good.variants.split(';')):
                found.append(good.name)
        if found:
            print(message.text, found)