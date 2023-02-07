# sanity check route
from flask import request

from app.main import bp
from database import Session
from app.wa_messages import get_messages, get_clients, get_clients_links, get_customers, get_payers
from app.models import ClientsLinks, ClientsLinksSchema

session = Session()


@bp.route('/', methods=['GET'])
def index():
    return "Hello World"


@bp.route('/messages', methods=['GET'])
def messages():
    return get_messages(session)


@bp.route('/clients', methods=['GET'])
def clients():
    return get_clients(session)


@bp.route('/customers', methods=['GET'])
def customers():
    return get_customers(session)


@bp.route('/payers', methods=['GET'])
def payers():
    return get_payers(session)


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
