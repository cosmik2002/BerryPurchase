import json
import re
from datetime import datetime
from typing import List

from sqlalchemy import not_, or_, Boolean

import PySimpleGUI as sg
from sqlalchemy.orm import aliased

from app.models import Customers, Messages, Goods, MessagesSchema, Clients, ClientsSchema, ClientsLinks, \
    ClientsLinksSchema, CustomersSchema, Payers, PayersSchema, GoodsSchema, MessageOrders, MessageOrdersSchema


def get_messages(session, message_id, search_options, page, page_size):
    query = session.query(Messages)
    if message_id:
        messages = query.get(message_id)
        messages_schema = MessagesSchema(exclude=('message_order',))
    else:
        if search_options['src']:
            # query = query.join(Customers, isouter=True)
            query = query.filter(Messages.text.like(f"{search_options}"))
        if search_options['has_order']:
            query = query.join(MessageOrders)
        if search_options['hide_empty']:
            query = query.filter(
                or_(Messages.props['empty'].as_string().cast(Boolean) == False, not_(Messages.props['empty'])))
        if search_options['start_date']:
            query = query.filter(Messages.timestamp >= search_options['start_date'])
        # query = query.order_by(Messages.timestamp.desc())

        # quoted = aliased(Messages)
        # query = query.join(quoted, Messages.props['quoted'].as_string() == quoted.wa_id).add_columns(quoted.text, quoted.id)

        query = query.order_by(Messages.timestamp)
        if page_size:
            query = query.limit(page_size)
            if page:
                query = query.offset((page - 1) * page_size)
        messages = query.all()
        # messages = session.query(Messages).order_by(Messages.timestamp.desc()).all()
        messages_schema = MessagesSchema(many=True, exclude=('message_order',))
    output = messages_schema.dump(messages)
    return output


def get_message_order(session, message_id, message_order_id, is_try_to_guess):
    if message_order_id:
        message_order = session.query(MessageOrders).get(message_order_id)
        message_order_schema = MessageOrdersSchema()
    else:
        message_order = session.query(MessageOrders).filter(MessageOrders.message_id == message_id).all()
        if is_try_to_guess and not message_order:
            message_order = try_to_guess(session, message_id)
        message_order_schema = MessageOrdersSchema(many=True)
    output = message_order_schema.dumps(message_order)
    return output


def try_to_guess(session, message_id):
    message: Messages = session.query(Messages).filter(Messages.id == message_id).one()
    goods: List[Goods] = session.query(Goods).all()
    found = []
    for good in goods:
        if good.active and message.text and any(word in message.text.lower()
                                                for word in (
                                                good.variants.split(';') if good.variants else good.name.lower().split(
                                                    ' ')) if len(word) > 2):
            found.append(good.id)
    if found:
        for good in found:
            session.add(MessageOrders(message_id=message_id, good_id=good, quantity=1))
        session.commit()
        return session.query(MessageOrders).filter(MessageOrders.message_id == message_id).all()
    return []


def load_clients(session):
    clients = session.query(Clients).order_by('name').all()
    clients_schema = ClientsSchema(many=True)
    output = clients_schema.dump(clients)
    return output


def load_customers(session):
    customers = session.query(Customers).all()
    customers_schema = CustomersSchema(many=True)
    output = customers_schema.dump(customers)
    return output


def load_payers(session):
    payers = session.query(Payers).all()
    payers_schema = PayersSchema(many=True)
    output = payers_schema.dump(payers)
    return output


def load_goods(session):
    goods = session.query(Goods).all()
    goods_schema = GoodsSchema(many=True)
    output = goods_schema.dump(goods)
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
