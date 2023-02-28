# sanity check route
import json
from pathlib import Path
from typing import Optional

from flask import request

from app.g_sheets import gSheets
from app.main import bp
from app.payment_messages import PaymentsProcessor
from app.whatsapp import WhatsApp
from database import Session
from app.wa_messages import get_messages, get_clients_links, load_customers, load_payers, load_clients, load_goods, \
    get_message_order
from app.models import ClientsLinks, ClientsLinksSchema, payers_to_clients, Payers, Clients, Customers, \
    MessageOrdersSchema

session = Session()
wa: Optional[WhatsApp] = None


@bp.route('/', methods=['GET'])
def index():
    return "Hello World"


@bp.route('/messages', methods=['GET'])
@bp.route('/messages/<message_id>', methods=['GET'])
def messages(message_id=None):
    return get_messages(session, message_id)


@bp.route('/message_order/<message_id>/<message_order_id>', methods=['GET'])
@bp.route('/message_order/<message_id>', methods=['GET'])
@bp.route('/message_order', methods=['POST'])
def message_order(message_id=None, message_order_id=None):
    response_object = {'status': 'success'}
    if request.method == 'POST':
        data = request.get_json()
        message_order_row = MessageOrdersSchema().load(data['message_order_row'], session=session)
        session.add(message_order_row)
        session.commit()
        return MessageOrdersSchema().dumps(message_order_row)
    else:
        return get_message_order(session, message_id, message_order_id)

@bp.route('/start_wa_client', methods=['GET'])
def start_wa_client():
    global wa
    wa = WhatsApp(session)
    return "ok"


@bp.route('/load_messages', methods=['GET'])
def load_messages():
    return wa.read_messages()


@bp.route('/parse_notify', methods=['GET'])
def parse_notify():
    counters = PaymentsProcessor().get_payment_messages()
    return json.dumps(counters)


@bp.route('/file_save', methods=['POST'])
def file_save():
    counters = None
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        counters = PaymentsProcessor().parse_sber_statement(uploaded_file.filename)
    return json.dumps(counters or {})


@bp.route('/clients', methods=['GET'])
def clients():
    return load_clients(session)


@bp.route('/get_clients', methods=['GET'])
def get_clients():
    return gSheets(session=session).get_clients()


@bp.route('/customers', methods=['GET'])
def customers():
    return load_customers(session)


@bp.route('/payers', methods=['GET'])
def payers():
    return load_payers(session)

@bp.route('/goods', methods=['GET'])
def goods():
    return load_goods(session)

@bp.route('/payments', methods=['GET'])
def payments():
    src = request.args.get('search')
    page = request.args.get('page', type=int)
    page_size = request.args.get('page_size', type=int)
    return PaymentsProcessor().get_payments(session, page, page_size, src)


@bp.route('/payers_to_clients', methods=['POST'])
def payers_to_clients():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        data = request.get_json()
        payer: Payers = session.query(Payers).get(data['payer_id'])
        client: Clients = session.query(Clients).get(data['client_id'])
        if payer.clients and payer.clients[0].id != client.id:
            payer.clients.remove(payer.clients[0])
        payer.clients.append(client)
        session.commit()
        response_object = {**response_object, ** data}
        return response_object

@bp.route('/customers_to_clients', methods=['POST'])
def customers_to_clients():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        data = request.get_json()
        customer: Customers = session.query(Customers).get(data['customer']['id'])
        client: Clients = session.query(Clients).get(data['client']['id'])
        if customer.clients and customer.clients[0].id != client.id:
            customer.clients.remove(customer.clients[0])
        customer.clients.append(client)
        session.commit()
        return response_object

@bp.route('/clients_links', methods=['GET', 'POST'])
def clients_link():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        data = request.get_json()
        if old_data := data.get('oldClientLink'):
            del data['oldClientLink']
            load_data = ClientsLinksSchema().load(data, session=session, instance=session.query(ClientsLinks).filter_by(
                client_id=old_data['client_id'], customer_id=old_data['customer_id'],
                payer_id=old_data['payer_id']).one())
        else:
            load_data = ClientsLinksSchema().load(data, session=session)
            session.add(load_data)
        session.commit()
        return response_object
    else:
        return get_clients_links(session)
