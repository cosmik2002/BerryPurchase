import datetime
import os

from flask import send_from_directory, current_app, request

from app.models import Settings, Itog, ItogSchema, MessageOrders, Messages
from app.reportsBp.reports import Reports
from app.reportsBp import bp


@bp.route('/client_good_report', methods=['GET'])
def client_good_report():
    r: Reports = Reports()
    r.fill_itog()
    report = r.create_report()
    return report


@bp.route('/client_payment_report', methods=['GET'])
def client_payment_report():
    r: Reports = Reports()
    r.fill_itog()
    report = r.get_itog()
    return report


@bp.route('/get_reports', methods=['GET'])
def get_reports():
    Reports().create_report(True)
    # uploads = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    uploads = os.path.join(os.getcwd(), current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(path="report.xlsx", directory=uploads)

@bp.route('/get_orders/<client_id>', methods=['GET'])
@bp.route('/get_orders/<client_id>/<good_id>', methods=['GET'])
def get_orders(client_id, good_id=None):
    return Reports().getMessages(client_id, good_id)


@bp.route('/get_itog/<sum>', methods=['GET'])
def get_itog(sum=None):
    start_date = current_app.session.query(Settings).filter(Settings.name == Settings.START_DATE).one()
    start_date = datetime.datetime.strptime(start_date.value, "%d.%m.%Y")
    itog = current_app.session.query(Itog).filter(Itog.date==start_date, Itog.sum==sum, Itog.client_id!=None, Itog.good_id==None).all()
    #asdict(itog[0]) #dataclass
    return ItogSchema(many=True).dump(itog)


@bp.route('/compare_reports', methods=['GET'])
def compare_reports():
    return Reports().compare_report()
