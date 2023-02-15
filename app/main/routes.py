# sanity check route
import json
from pathlib import Path

from flask import request

from app.g_sheets import gSheets
from app.main import bp
from app.payment_messages import PaymentsProcessor
from database import Session
from app.wa_messages import get_messages, get_clients_links, load_customers, load_payers, load_clients
from app.models import ClientsLinks, ClientsLinksSchema

session = Session()


@bp.route('/', methods=['GET'])
def index():
    return "Hello World"


@bp.route('/messages', methods=['GET'])
def messages():
    return get_messages(session)


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


@bp.route('/clients_links', methods=['GET', 'POST'])
def clients_link():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        load_data = ClientsLinksSchema().load(request.get_json(), session=session)
        session.add(load_data)
        session.commit()
        return response_object
    else:
        return get_clients_links(session)
