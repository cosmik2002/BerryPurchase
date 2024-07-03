import datetime
import os

from flask import send_from_directory, current_app, request

from app import wa
from app.models import Settings, Itog, ItogSchema, MessageOrders, Messages, Customers
from app.reportsBp.reports import Reports
from app.reportsBp import bp
from app.telegram_api import TelegramApi


@bp.route('/client_good_report', methods=['GET'])
def client_good_report():
    '''получет основной отчет с оплатами'''
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y")
    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y")
    r: Reports = Reports(start_date, end_date)
    r.fill_itog()
    report = r.create_report(False)
    return report


@bp.route('/client_payment_report', methods=['GET'])
def client_payment_report():
    r: Reports = Reports()
    r.fill_itog()
    report = r.get_itog()
    return report


@bp.route('/get_reports', methods=['GET'])
def get_reports():
    '''получает файл отчета'''
    Reports().create_report(True)
    # uploads = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    uploads = os.path.join(os.getcwd(), current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(path="report.xlsx", directory=uploads)


@bp.route('/get_orders/<client_id>', methods=['GET'])
@bp.route('/get_orders/<client_id>/<good_id>', methods=['GET'])
def get_orders(client_id, good_id=None):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y")
    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y")
    return Reports(start_date, end_date).getMessages(client_id, good_id)


@bp.route('/send', methods=['POST'])
def send():
    if request.method == 'POST':
        data = request.get_json()
        cust: Customers = current_app.session.query(Customers).get(data['customer'])
        if cust.params and cust.params.get('from') == 'whatsapp':
            wa.send_message(cust.wa_id, data['text'])
        else:
            cust: Customers = current_app.session.query(Customers).get(154)
            TelegramApi().send(int(cust.wa_id), data['text'])
    return ''


@bp.route('/get_itog/<sum>', methods=['GET'])
def get_itog(sum=None):
    '''получает заказы по сумме'''
    start_date = current_app.session.query(Settings).filter(Settings.name == Settings.START_DATE).one()
    start_date = datetime.datetime.strptime(start_date.value, "%d.%m.%Y")
    itog = current_app.session.query(Itog).filter(Itog.date == start_date, Itog.sum == sum, Itog.client_id != None,
                                                  Itog.good_id == None).all()
    # asdict(itog[0]) #dataclass
    return ItogSchema(many=True).dump(itog)


@bp.route('/compare_reports', methods=['GET'])
def compare_reports():
    return Reports().compare_report()
