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
from app.wa_messages import get_messages, get_clients_links, load_customers, load_payers, load_clients
from app.models import ClientsLinks, ClientsLinksSchema, payers_to_clients, Payers, Clients

session = Session()
wa: Optional[WhatsApp] = None


@bp.route('/', methods=['GET'])
def index():
    return "Hello World"


@bp.route('/messages', methods=['GET'])
def messages():
    return get_messages(session)


# @bp.route('/get_message_orders', methods=['GET'])
# def messages():
#     return get_messages(session)

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
    return gSheets.get_clients(session)


@bp.route('/customers', methods=['GET'])
def customers():
    return load_customers(session)


@bp.route('/payers', methods=['GET'])
def payers():
    return load_payers(session)


@bp.route('/payments', methods=['GET'])
def payments():
    return PaymentsProcessor().get_payments(session)


@bp.route('/payers_to_clients', methods=['POST'])
def payers_to_clients():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        data = request.get_json()
        payer: Payers = session.query(Payers).get(data['payer']['id'])
        client: Clients = session.query(Clients).get(data['client']['id'])
        if payer.clients and payer.clients[0].id != client.id:
            payer.clients.remove(payer.clients[0])
        payer.clients.append(client)
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
