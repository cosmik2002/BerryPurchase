import os
import re
import camelot
import pandas as pd


# pip install camelot-py[cv]
# pip install pypdf
# https://github.com/camelot-dev/camelot/issues/339#issuecomment-1368217259

class ReadSberStatementPdf:

    def __init__(self):
        self.csv_filename = None

    def read_and_parse_doc(self, filename):
        pre, ext = os.path.splitext(filename)
        self.csv_filename = pre + '.csv'
        df = self.parse_tables(filename)
        result = self.prepare_result(df)
        result.to_csv(self.csv_filename, index=False)
        return result

    def parse_tables(self, filename):
        # edge_tol вертикальное расстояние между строк (default=50)
        # когда выписка заканчивается на стр. с реквизитами, чтобы не сливал в одну таблицк
        tables = camelot.read_pdf(filename, pages='1-end', flavor='stream', edge_tol=40)
        result = pd.DataFrame()
        for table in tables:
            if table.order == 1:
                result = pd.concat([result, table.df])
        result = result.rename(columns={0: 'date_code', 1: 'name', 2: 'sum'})
        return result

    def prepare_result(self, tab):
        tab = tab[tab['date_code'].str.contains('^\d{2}\.\d{2}\.\d{2}.*')]
        tab = tab.reset_index(drop=True)
        # SettingWithCopyWarning:
        # tab['date'] = pd.to_datetime(tab.loc[tab.index % 2 == 0, '0'], format="%d.%m.%Y\n%H:%M")
        tab = tab.assign(date=pd.to_datetime(tab.loc[tab.index % 2 == 0, 'date_code'], format="%d.%m.%Y\n%H:%M"))
        tab['date1'] = pd.to_datetime(tab[tab.index % 2 == 1]['date_code'].str[0:10], format="%d.%m.%Y")
        tab['code'] = tab[tab.index % 2 == 1]['date_code'].str[11:]
        tab['card_number'] = tab[tab.index % 2 == 1]['name'].apply(
            lambda x: r.group(0) if (r := re.search('(\d{4})\*\*\*\*(\d{4})', x)) is not None else '')
        # 'NO-BREAK SPACE' u'\xa0'
        tab['summa'] = tab.loc[tab.index % 2 == 0, 'sum'].apply(lambda x:
                                                                float(x[1:].replace(',', '.').replace(u'\xa0',
                                                                                                      '')) if x.startswith(
                                                                    '+') else float(
                                                                    x.replace(',', '.').replace(u'\xa0', '')) * -1)
        # "SBOL перевод 4276****6624 Р. МАКСИМ ВАЛЕРЬЕВИЧ"
        tab['payer'] = tab[tab.index % 2 == 1]['name'].apply(
            lambda x: (f"{r.group(2)} {r.group(3)} {r.group(1)}") if (r := re.search('(\w)\.\s(\w+)\s(\w+)$',
                                                                                     x)) is not None else '')
        # тут в лямбду передается Series из двух ячеек для группировки
        tab = tab.groupby(tab.index // 2).agg(lambda x: x.dropna().astype(str).str.cat(sep=','))
        tab['date'] = tab['date'].astype('datetime64[ns]')
        tab['date1'] = tab['date1'].astype('datetime64[ns]')
        return tab


if __name__ == "__main__":
    ReadSberStatementPdf().read_and_parse_doc(r'..\Документ-2023-02-06-071313.pdf')
