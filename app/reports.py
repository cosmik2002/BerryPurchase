import os
from collections import defaultdict
from pathlib import Path

import pandas as pd
import simplejson
from flask import current_app
from pandas import DataFrame as df
from sqlalchemy import func, text
from sqlalchemy.orm import aliased

from app.g_sheets import gSheets
from app.models import MessageOrders, Messages, Goods, Settings, Clients, Customers
from datetime import datetime as dt
import json


class Reports:
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
