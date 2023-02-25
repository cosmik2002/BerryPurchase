from app.models import Clients
import pygsheets


class gSheets:
    def __init__(self, session):
        self.session = session

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
        wks = sh.worksheet('index', 1)
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
