import decimal
import itertools
import json
from datetime import datetime as dt
from typing import List

import numpy as np
import pandas as pd
from tqdm import tqdm

from app.models import Clients, Settings, Payments
import pygsheets
from pygsheets.worksheet import Worksheet


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class gSheets:
    def __init__(self, session):
        self.session = session
        self.workbook_name = '2024 УРБАНЫ'

    def open_sheet(self):
        sheet_name = self.session.query(Settings).filter(Settings.name == Settings.SHEET_NAME).one().value
        client = pygsheets.authorize(service_file=r'lucid-access-99211-bd2544a973ad.json')
        sh = client.open(self.workbook_name)
        wks: Worksheet = sh.worksheet('title', sheet_name)
        return wks

    def get_summary(self):
        '''список на раздачу'''
        wks = self.open_sheet()
        df = wks.get_as_df(start='A2')
        df = df.replace('', None)
        start_col = 2 if df.values[0][1] is None else 1
        clients = wks.get_values('A', 'A')
        clients = list(itertools.chain.from_iterable(clients))
        last_row = df[(df['имя'].values != None)].index[-1]  # name col last index
        price_row = df.iloc[1, :].values
        last_col = len(price_row[price_row != None])
        # last_col = len(df.iloc[1, :][(df.iloc[1, :].values != None)]) #price row len
        good_tr = df[2:last_row + 1].melt(id_vars=['имя'], value_vars=df.columns[start_col:last_col])
        # меняем , на .
        good_tr = good_tr.replace(to_replace={'value': r','}, value={'value': '.'}, regex=True)
        good_tr = good_tr.replace(to_replace={'value': ' '}, value={'value': None})
        cli_itog = good_tr[good_tr['value'].astype('float') > 0].assign(
            res=lambda x: x['variable'].astype(str) + "-" + x['value'].astype('float').map('{:g}'.format)).groupby(
            'имя').agg({'res': lambda x: ",".join(x)})
        df.iloc[2:last_row + 1, start_col:last_col] = df.iloc[2:last_row + 1, start_col:last_col].replace(' ', value=None)
        good_itog = df.iloc[2:last_row + 1, start_col:last_col].replace(regex=',', value='.').astype('float').sum()
        res = pd.concat([cli_itog, good_itog])
        return res.to_json()

    def fill_payments(self):
        start_date = self.session.query(Settings).filter(Settings.name == Settings.START_DATE).one()
        start_date = dt.strptime(start_date.value, "%d.%m.%Y")
        sheet_name = self.session.query(Settings).filter(Settings.name == Settings.SHEET_NAME).one().value
        payments: List[Payments] = self.session.query(Payments).filter(Payments.timestamp > start_date).all()
        client = pygsheets.authorize(service_file=r'lucid-access-99211-bd2544a973ad.json')
        sh = client.open(self.workbook_name)
        wks: Worksheet = sh.worksheet('title', sheet_name)
        rng = wks.get_values('2', '2')
        last_col = len(rng[0])
        clients = wks.get_values('A', 'A')
        clients = list(itertools.chain.from_iterable(clients)) #делаем список из списка списков
        last_row = len(clients)
        values = [['', float(0)] for x in range(1, last_row+1)]
        for payment in tqdm(payments):
            if not payment.payer:
                continue
            if payment.payer.clients:
                if payment.payer.clients[0].name in clients:
                    i = clients.index(payment.payer.clients[0].name)
                    values[i][1] += float(payment.sum)
                else:
                    print(payment.id)
                    values.append([payment.payer.clients[0].name, float(payment.sum)])
        wks.update_values((1, last_col), values)

    def get_clients(self):
        counters = {
            'all': 0,
            'new_clients': 0,
            'found': 0
        }
        client = pygsheets.authorize(service_file=r'lucid-access-99211-bd2544a973ad.json')

        # t = client.spreadsheet_titles()
        # print (t)
        # t = client.spreadsheet_ids()
        # print (t)
        # Open the spreadsheet and the first sheet.
        sh = client.open('2024 УРБАНЫ')
        # wks = sh.sheet1
        sheet_name = self.session.query(Settings).filter(Settings.name == Settings.SHEET_NAME).one().value
        wks = sh.worksheet('title', sheet_name)
        header = wks.cell('A2')
        # rng = wks.get_values('A1', 'AI51', returnas='range')
        # rng = wks.get_all_values()
        df = wks.get_as_df(start='A2')
        clients = df.iloc[3:, 0]
        rng = wks.get_values('A', 'A', returnas='range')
        for client in clients:
            if not client:
                continue
            counters['all'] = counters['all'] + 1
            cli = self.session.query(Clients).filter_by(name=client).all()
            if not cli:
                new_client = Clients(name=client)
                self.session.add(new_client)
                self.session.commit()
                counters['new_clients'] = counters['new_clients'] + 1
            else:
                counters['found'] += 1
        return counters
