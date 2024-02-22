import os
from collections import defaultdict
from pathlib import Path

import pandas as pd
import simplejson
from flask import current_app
from pandas import DataFrame as df
from sqlalchemy import func, text, select
from sqlalchemy.orm import aliased, Session

from app.g_sheets import gSheets
from app.models import MessageOrders, Messages, Goods, Settings, Clients, Customers, Itog, Payers, Payments
from datetime import datetime as dt
import json


class Reports:

    def get_itog(self):
        session: Session = current_app.session
        start_date = session.query(Settings).filter(Settings.name == Settings.START_DATE).one()
        start_date = dt.strptime(start_date.value, "%d.%m.%Y")

        payments_subquery = select(func.coalesce(Payments.for_client_id, Clients.id).label('p_client_id'),func.sum(Payments.sum).label('p_sum')).join(Payers).join(Clients, Payers.clients)\
            .filter(Payments.timestamp>=start_date).group_by(text("1")).subquery()

        query = select(Clients.name, func.sum(Itog.org),func.sum(Itog.sum), func.sum(payments_subquery.c.p_sum))\
            .join(Clients).join(payments_subquery, Itog.client_id==payments_subquery.c.p_client_id, isouter=True)\
            .filter(Itog.date==start_date, Itog.good_id==None).group_by(text("1"))
        result_q = session.execute(query)
        result = []
        for row in result_q.mappings():
            result.append(dict(row))
        return result

    def fill_itog(self):
        session: Session = current_app.session
        start_date = session.query(Settings).filter(Settings.name == Settings.START_DATE).one()
        start_date = dt.strptime(start_date.value, "%d.%m.%Y")
        for_client = aliased(Clients)
        query = session.query(MessageOrders).join(Messages).join(Goods) \
            .join(Customers).join(Clients, Customers.clients, isouter=True).join(Messages.for_client.of_type(for_client), isouter=True) \
            .with_entities(Goods.id.label('good_id'),func.coalesce(Goods.price, 0).label('price'),func.coalesce(Goods.org_price, 0).label('org'), func.coalesce(for_client.id, Clients.id).label('client_id'),
                           func.sum(MessageOrders.quantity).label('count')).filter(
            Messages.timestamp >= start_date).group_by(text("1,2,3,4")).order_by(Goods.type)
        session.query(Itog).filter(Itog.date==start_date).delete()
        all = query.all()
        for row in all:
            sum = row.count * (row.org+row.price)
            session.add(Itog(date=start_date, client_id=row.client_id, good_id=row.good_id, quantity=row.count, price=row.price, org=row.org, sum=sum))
        session.commit()
        res = session.execute(text(
            f"insert into itog (date, client_id, org, sum) select date, client_id, sum(org),sum(sum) from itog where date(date)=date('{start_date.strftime('%Y-%m-%d')}') and client_id is not null and good_id is not null  group by 1,2"))
        session.execute(text(
            f"insert into itog (date, good_id,price, org, quantity, sum) select date, good_id, price, org,sum(quantity),sum(sum) from itog where date(date)=date('{start_date.strftime('%Y-%m-%d')}') and client_id is not null and good_id is not null group by 1,2,3,4"))
        session.commit()

    def create_report(self):
        session = current_app.session
        # summary = gSheets(session).get_summary()
        start_date = session.query(Settings).filter(Settings.name == Settings.START_DATE).one()
        start_date = dt.strptime(start_date.value, "%d.%m.%Y")
        settings = session.query(Settings)
        goods = session.query(Goods).all()
        for_client = aliased(Clients)
        query = session.query(MessageOrders).join(Messages).join(Goods) \
            .join(Customers).join(Clients, Customers.clients, isouter=True).join(Messages.for_client.of_type(for_client), isouter=True) \
            .with_entities(func.coalesce(Goods.short_name, Goods.name).label('good'),func.coalesce(Goods.price, 0).label('price'), func.coalesce(for_client.name, Clients.name).label('client'),
                           func.sum(MessageOrders.quantity).label('count')).filter(
            Messages.timestamp >= start_date).group_by(text("1,2,3")).order_by(Goods.type)
        result = []
        for row in query.all():
            result.append(dict(row._mapping))

        df = pd.read_json(simplejson.dumps(result))
        df=df.pivot(index='client', columns=['good', 'price'], values='count')
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'report.xlsx')
        df.to_excel(path)
        return result

    def compare_report(self):
        session = current_app.session
        summary = gSheets(session).get_summary()
        # summary = json.loads(summary)
        report = self.create_report()
        clients = defaultdict(lambda: defaultdict(int))
        goods = defaultdict(int)
        clients_gs = defaultdict(lambda: defaultdict(int))
        for row in summary[1]:
            if row['value'] > 0:
                clients_gs[row['имя']][row['variable']] += row['value']
        for row in report:
            clients[row['client']][row['good']] += 1
            goods[row['good']] += 1
        result = {
            'goods': goods,
            'clients': clients,
            'gs_goods': summary[2],
            'gs_clients': clients_gs
        }
        return result
