import datetime
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import simplejson
from flask import current_app
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from pandas import DataFrame as df
from sqlalchemy import func, text, select, Integer, Float, String
from sqlalchemy.orm import aliased, Session

from app.g_sheets import gSheets
from app.models import MessageOrders, Messages, Goods, Settings, Clients, Customers, Itog, Payers, Payments, \
    customers_to_clients, payers_to_clients
from datetime import datetime as dt
import json


class Reports:

    def get_itog(self):
        session: Session = current_app.session
        start_date = session.query(Settings).filter(Settings.name == Settings.START_DATE).one()
        start_date = dt.strptime(start_date.value, "%d.%m.%Y")

        payments_subquery = select(func.coalesce(Payments.for_client_id, Clients.id).label('p_client_id'),
                                   func.sum(Payments.sum).label('p_sum')).join(Payers).join(Clients, Payers.clients) \
            .filter(Payments.timestamp >= start_date, func.coalesce(Payments.not_use, False) == False).group_by(
            text("1")).subquery()

        query = select(Clients.name, func.sum(Itog.org), func.sum(Itog.sum), func.sum(payments_subquery.c.p_sum),
                       func.sum(Itog.sum - payments_subquery.c.p_sum)) \
            .join(Clients).join(payments_subquery, Itog.client_id == payments_subquery.c.p_client_id, isouter=True) \
            .filter(Itog.date == start_date, Itog.good_id == None).group_by(text("1"))
        result_q = session.execute(query)
        result = []
        for row in result_q.mappings():
            result.append(dict(row))
        return result

    def getMessages(self, client_id, good_id=None):
        start_date = current_app.session.query(Settings).filter(Settings.name == Settings.START_DATE).one()
        start_date = dt.strptime(start_date.value, "%d.%m.%Y")
        for_client = aliased(Clients)
        good_id = int(good_id) if good_id else None
        query = select(Messages.text.label("1Сообщение"), Messages.props['comment'].as_string().label("4Коммент"),
                       func.strftime('%d.%m.%Y %H:%M', Messages.timestamp).label("2Дата"), func.aggregate_strings(Goods.name+'-'+func.cast(MessageOrders.quantity, String), ';').label("3Заказ"))\
            .select_from(MessageOrders).join(Messages).join(Goods) \
            .join(Customers).join(customers_to_clients, isouter=True).join(Clients, func.coalesce(Messages.for_client_id, customers_to_clients.c.client_id) == Clients.id) \
            .filter(Messages.timestamp >= start_date, func.coalesce(Clients.duplicate_for, Clients.id) == int(client_id),
                                                                          Goods.id == func.coalesce(good_id, Goods.id)).group_by(text("1, 2, 3"))
        results = [dict(row) for row in current_app.session.execute(query).mappings()]
        return results

    def fill_itog(self):
        session: Session = current_app.session
        start_date = session.query(Settings).filter(Settings.name == Settings.START_DATE).one()
        start_date = dt.strptime(start_date.value, "%d.%m.%Y")
        for_client = aliased(Clients)
        query = session.query(MessageOrders).join(Messages).join(Goods) \
            .join(Customers).join(Clients, Customers.clients, isouter=True).join(
            Messages.for_client.of_type(for_client), isouter=True) \
            .with_entities(Goods.id.label('good_id'), func.coalesce(Goods.price, 0).label('price'),
                           func.coalesce(Goods.org_price, 0).label('org'),
                           func.coalesce(for_client.id, Clients.id).label('client_id'),
                           func.sum(MessageOrders.quantity).label('count')).filter(
            Messages.timestamp >= start_date).group_by(text("1,2,3,4")).order_by(Goods.type)
        session.query(Itog).filter(Itog.date == start_date, Itog.type == Itog.CALCULATED).delete()
        all = query.all()
        for row in all:
            sum = row.count * (row.org + row.price)
            session.add(
                Itog(date=start_date, client_id=row.client_id, good_id=row.good_id, quantity=row.count, price=row.price,
                     org=row.org, sum=sum, type=Itog.CALCULATED))
        session.commit()
        res = session.execute(text(
            f"insert into itog (date, client_id, org, sum, type) select date, client_id, sum(org),sum(sum), {Itog.CALCULATED} from itog where date(date)=date('{start_date.strftime('%Y-%m-%d')}') and client_id is not null and good_id is not null and type={Itog.CALCULATED} group by 1,2"))
        session.execute(text(
            f"insert into itog (date, good_id,price, org, quantity, sum, type) select date, good_id, price, org,sum(quantity),sum(sum), {Itog.CALCULATED} from itog where date(date)=date('{start_date.strftime('%Y-%m-%d')}') and client_id is not null and good_id is not null and type={Itog.CALCULATED} group by 1,2,3,4"))
        session.commit()

    def create_report(self, to_excel=False):
        session = current_app.session
        # summary = gSheets(session).get_summary()
        start_date = session.query(Settings).filter(Settings.name == Settings.START_DATE).one()
        start_date = dt.strptime(start_date.value, "%d.%m.%Y")
        settings = session.query(Settings)
        goods = session.query(Goods).all()
        for_client = aliased(Clients)
        payments_query = select(func.coalesce(Clients.duplicate_for, Clients.id).label('client_id'),
                                func.sum(Payments.sum).label('p_sum')).join(Payers).join(payers_to_clients, isouter=True).\
            join(Clients, func.coalesce(Payments.for_client_id, payers_to_clients.c.client_id)==Clients.id) \
            .filter(Payments.timestamp >= start_date, func.coalesce(Payments.not_use, False) == False).group_by(
            text("1"))

        # query = select(Clients.id.label('client_id'), Goods.name.label('good'), Goods.price, Itog.quantity.label('count'), Itog.sum)\
        #     .join(Clients).join(Goods).filter(Itog.date==start_date, Itog.type==Itog.CALCULATED).order_by(Goods.type)

        query = select(func.coalesce(Goods.short_name, Goods.name).label('good'),
                       Goods.id.label('good_id'),
                       func.cast(func.coalesce(Goods.price, 0), Integer).label('price'),
                       func.coalesce(Goods.weight, 0).label('weight'),
                       func.cast(func.coalesce(Goods.org_price, 0), Integer).label('org_price'),
                       func.coalesce(Clients.duplicate_for, Clients.id).label('client_id'),
                       func.coalesce(Goods.active, False).label('active'),
                       func.cast(func.sum(MessageOrders.quantity), Float).label('count'),
                       func.aggregate_strings(Messages.props['comment'].as_string(), ";").label('comment'),
                       # кастим во float, иначе в pandas тип будет object и в excel выгрузятся с ,
                       func.sum(MessageOrders.quantity * Goods.price + MessageOrders.quantity * Goods.org_price).label(
                           'sum')) \
            .select_from(MessageOrders) \
            .join(Messages).join(Customers).join(customers_to_clients, isouter=True).join(Goods) \
            .join(Clients, func.coalesce(Messages.for_client_id, customers_to_clients.c.client_id) == Clients.id) \
            .filter(Messages.timestamp >= start_date).group_by(text("1,2,3,4,5,6,7")).order_by(Goods.type)
        sum_query = select(
            func.coalesce(Messages.for_client_id, customers_to_clients.c.client_id).label('client_id'),
            func.sum(MessageOrders.quantity * Goods.price + MessageOrders.quantity * Goods.org_price).label('sum')) \
            .select_from(MessageOrders) \
            .join(Messages).join(Customers).join(customers_to_clients, isouter=True).join(Goods) \
            .filter(Messages.timestamp >= start_date).group_by(text("1"))

        # result = []
        # for row in session.execute(query).mappings():
        #     result.append(dict(row))

        df = pd.DataFrame.from_records(session.execute(query).mappings())
        payments = pd.read_sql(payments_query, session.bind, index_col="client_id")
        # payments.columns = pd.MultiIndex.from_product([payments.columns, [0], [0]])
        df['weight'] = df['weight'].astype(float)
        payments.columns = pd.MultiIndex.from_product([[''], ['Оплаты'], [''], [''], ['']])
        # sum=df.pivot(index='client_id', columns=['good', 'weight', 'price', 'org_price'], values='sum')
        sum = df.groupby('client_id').sum()['sum'].to_frame()
        sum['sum'] = sum['sum'].astype('float')
        sum.columns = pd.MultiIndex.from_product([[''], sum.columns, [''], [''], ['']])
        comm = df.groupby('client_id').max()['comment'].to_frame()
        comm.columns = pd.MultiIndex.from_product([[''], comm.columns, [''], [''], ['']])

        df = df.pivot(index='client_id', columns=['good_id', 'good', 'weight', 'price', 'org_price'], values='count')
        if not to_excel:
            df = df.merge(sum, how="left", left_index=True, right_index=True)
        df = df.merge(comm, how="left", left_index=True, right_index=True)
        df = df.merge(payments, how="left", left_index=True, right_index=True)
        clients = pd.DataFrame.from_records(session.execute(select(Clients.id, Clients.name)).mappings(), index='id')
        clients.columns = pd.MultiIndex.from_product([[''], clients.columns, [''], [''], ['']])
        df = df.merge(clients, left_index=True, right_index=True)
        df['', 'client_id', '', '', ''] = df.index
        df.index = df['']['name']  # ['']['']['']['']
        df = df.drop(('', 'name', '', '', ''), axis=1)
        df = df.sort_index()

        if to_excel:

            df.columns = df.columns.droplevel()  # убираем ид товара из первой строки
            df = df.drop(('client_id', '', '', ''), axis=1)
            # оплаты в конец
            column_to_move = df.pop(("Оплаты", '', '', ''))
            commen_col = df.pop(("comment", '', '', ''))
            # разные варианты обавления формул (сразу в фрейм или потом в excel)
            col_l = get_column_letter(len(df.columns) + 1)
            df['Стоим.', '', '', ''] = [f"=SUMPRODUCT(B4:{col_l}4,B{i + 6}:{col_l}{i + 6})" for i in np.arange(len(df))]
            # так работает R1C1 INDIRECT
            # df['Стоим.', '', '', ''] = f'=SUMPRODUCT(INDIRECT("R4C2",0):INDIRECT("R4C[-1]",0), INDIRECT("RC2",0):INDIRECT("RC[-1]",0))'
            df['Орг.', '', '', ''] = None
            df['К оплате', '', '', ''] = None
            df.insert(len(df.columns), "Оплаты", column_to_move)
            df.insert(len(df.columns), "comment", commen_col)

            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'report.xlsx')
            styled = df.style.apply_index(lambda x: [f'text-align: left; font-weight: bold' for v in x], axis="rows")
            sheet_name = "Список"
            with pd.ExcelWriter(path) as wb:
                styled.to_excel(wb, sheet_name=sheet_name, startrow=1)
                sheet: Worksheet = wb.book.worksheets[0]
                sheet['A2'].value = "Имя"
                sheet['A3'].value = "Вес"
                sheet['A4'].value = "Цена"
                sheet['A5'].value = "Орг."
                sheet.delete_rows(6)
                r = sheet.max_row
                c = sheet.max_column
                # имя, стоим, орг, к оплате,  оплаты, коммент
                col_sum_l = get_column_letter(c - 4)
                col_org_l = get_column_letter(c - 3)
                col_itog_l = get_column_letter(c - 2)
                cmaxl = get_column_letter(c - 5)
                # сумма
                # for i in range(6, r + 1):
                #     sheet[f'{col_sum_l}{i}'].value = f"=SUMPRODUCT(B4:{cmaxl}4,B{i}:{cmaxl}{i})"
                # орг
                for i in range(6, r + 1):
                    sheet[f'{col_org_l}{i}'].value = f"=SUMPRODUCT(B5:{cmaxl}5,B{i}:{cmaxl}{i})"
                # итог по клиенту
                for i in range(6, r + 1):
                    sheet[f'{col_itog_l}{i}'].value = f"=SUM({col_sum_l}{i}:{col_org_l}{i})"
                # суммы к оплате
                for i in range(2, c):
                    col_sum_l = get_column_letter(i)
                    sheet[f'{col_sum_l}{r + 1}'].value = f"=SUM({col_sum_l}6:{col_sum_l}{r})"

        return df.to_json(orient='index')

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
