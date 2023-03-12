import decimal
import itertools
from datetime import datetime as dt
from typing import List

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

    def fill_payments(self):
        start_date = self.session.query(Settings).filter(Settings.name==Settings.START_DATE).one()
        start_date = dt.strptime(start_date.value, "%d.%m.%Y")
        sheet_name = self.session.query(Settings).filter(Settings.name==Settings.SHEET_NAME).one().value
        payments: List[Payments] = self.session.query(Payments).filter(Payments.timestamp>start_date).all()
        client = pygsheets.authorize(service_file=r'lucid-access-99211-bd2544a973ad.json')
        sh = client.open('Урбаны 2023')
        wks: Worksheet = sh.worksheet('title',sheet_name)
        mtd = wks.get_developer_metadata()
        rng = wks.get_values('2', '2')
        last_col = len(rng[0])
        clients = wks.get_values('A', 'A')
        clients = list(itertools.chain.from_iterable(clients))
        last_row = len(clients)
        # wks.update_values((last_row,last_row), None)
        # vals = wks.get_values((1, last_row), (last_col, last_row))
        wks.clear((1, last_col), (last_row, last_col))
        # wks.clear((1, 52), (last_col, 52))
        for payment in tqdm(payments):
            if payment.payer.clients:
                if payment.payer.clients[0].name in clients:
                    i = clients.index(payment.payer.clients[0].name)
                    val = wks.cell((i + 1, last_col)).value
                    if is_number(val):
                        val = decimal.Decimal(val) + payment.sum
                    else:
                        val = payment.sum
                    wks.cell((i + 1, last_col)).set_value(f"{val:g}".replace('.', ','))



    def get_clients(self):
        counters = {
            'all':0,
            'new_clients': 0,
            'found': 0
        }
        client = pygsheets.authorize(service_file=r'lucid-access-99211-bd2544a973ad.json')

        # t = client.spreadsheet_titles()
        # print (t)
        # t = client.spreadsheet_ids()
        # print (t)
        # Open the spreadsheet and the first sheet.
        sh = client.open('Урбаны 2023')
        # wks = sh.sheet1
        sheet_name = self.session.query(Settings).filter(Settings.name==Settings.SHEET_NAME).one().value
        wks = sh.worksheet('title',sheet_name)
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
