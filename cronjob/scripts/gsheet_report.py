import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
from pymongo import MongoClient
import os
import time

logger = logging.getLogger(__name__)


class GoogleSheetsReport():
    def __init__(self):
        self.secret_file = (os.path.dirname(os.path.abspath(__file__))
                            + '/client_secret.json')
        self.sheet_id = os.getenv("SHEET_ID", "")
        self.header = {'Proposição': 1, 'Tramitação': 2, 'Apreciação': 3,
                       'Situação': 4, 'Ementa': 5, 'Autor': 6,
                       'Partido_autor': 7, 'Estado_autor': 8, 'Relator': 9,
                       'Partido_relator': 10, 'Estado_relator': 11,
                       'Apensados': 12}

    def connect_to_db(self):
        TELEGRAM_DB_URI = os.getenv("TELEGRAM_DB_URI", "")
        client = MongoClient(TELEGRAM_DB_URI)
        db = client["bot"]
        return db

    def connect_sheet(self):
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        try:
            creds = ServiceAccountCredentials\
                            .from_json_keyfile_name(self.secret_file,
                                                    scope)
            client = gspread.authorize(creds)
        except ValueError:
            logger.error(ValueError)
        try:
            sheet = client.open_by_key(self.sheet_id).sheet1
        except ValueError:
            logger.error(ValueError)
        return sheet

    def get_todays_pls(self, db):
        # today = datetime.date.today().strftime("%d/%m/%Y")
        today = "18/09/2019"
        projects = db["Project"]
        query = {"data": today}
        today_pls = projects.find(query)
        pls_list = []
        for pl in today_pls:
            pls_list.append(pl)
        return pls_list

    def write_header(self, sheet):
        if not (self.header_exists(sheet)):
            for key in self.header:
                sheet.update_cell(1, self.header[key], key)

    def header_exists(self, sheet):
        sheet_data = sheet.get_all_values()
        try:
            if len(sheet_data) == 0 and\
               not(sheet_data[0] == list(self.header.values())):
                return False
            else:
                return True
        except IndexError:
            return False

    def get_sheet_rows_num(self, sheet):
        return len(sheet.get_all_values())

    def dict_query_db(self, today_pls, index):
        dict_query = self.header
        hiperlynk_str = '=HIPERLINK("{url}";"{value}")'
        if today_pls[index]['relator']['id']:
            list_query = [hiperlynk_str.format(
                        url=today_pls[index]['urlPL'],
                        value=today_pls[index]['sigla'] + ' ' +
                        str(today_pls[index]['numero'])
                        + '/' + str(today_pls[index]['ano'])),
                        today_pls[index]['regime'],
                        '-', today_pls[index]['situacao'],
                        today_pls[index]['ementa'],
                        hiperlynk_str.format(
                        url=today_pls[index]['autor']['urlDeputado'],
                        value=today_pls[index]['autor']['nome'],
                        ),
                        today_pls[index]['autor']['siglaPartido'],
                        today_pls[index]['autor']['estado'],
                        hiperlynk_str.format(
                            url=today_pls[index]['relator']['urlRelator'],
                            value=today_pls[index]['relator']['nome'],
                        ),
                        today_pls[index]['relator']['siglaPartido'],
                        today_pls[index]['relator']['estado'],
                        '-']
        else:
            list_query = [hiperlynk_str.format(
                        url=today_pls[index]['urlPL'],
                        value=today_pls[index]['sigla'] + ' ' +
                        str(today_pls[index]['numero'])
                        + '/' + str(today_pls[index]['ano'])),
                        today_pls[index]['regime'],
                        '-', today_pls[index]['situacao'],
                        today_pls[index]['ementa'],
                        hiperlynk_str.format(
                        url=today_pls[index]['autor']['urlDeputado'],
                        value=today_pls[index]['autor']['nome'],
                        ),
                        today_pls[index]['autor']['siglaPartido'],
                        today_pls[index]['autor']['estado'],
                        today_pls[index]['relator']['nome'],
                        today_pls[index]['relator']['siglaPartido'],
                        today_pls[index]['relator']['estado'],
                        '-']
        for dict_key, db_query in zip(list(dict_query.keys()), list_query):
            dict_query[dict_key] = db_query
        return dict_query

    def write_pls_report(self, db, today_pls, rows_num, sheet):
        col = 1
        for i, _ in enumerate(today_pls):
            query_results = self.dict_query_db(today_pls, i)
            for key in query_results:
                sheet.update_cell(rows_num + 1 + i, col,
                                  query_results[key])
                time.sleep(2)  # sleep to avoid sheets api request limit
                col += 1
            col = 1


# {
#     "proposicao": "{sigla} + {numero}/{ano}",
#     "tramitacao": "statusProposicao['regime']",
#     "apreciacao": "pegar do site (forma de apreciacao)",
#     "situacao": "despacho?",# atual tramitacao do banco
#     "ementa": "dados['ementa']",
#     "autor": "requisicao para a api,
#     "partido": "segue o do autor",
#     "estado": "segue o do autor",
#     "relator": "fazer req com o link do campo de relator,
#     "partido": "segue o do relator",
#     "estado": "segue o do estado",
#     "apensados": "pegar do site (apensados)"
# }

if __name__ == "__main__":
    gs = GoogleSheetsReport()
    db = gs.connect_to_db()
    today_pls = gs.get_todays_pls(db)
    sheet = gs.connect_sheet()
    gs.write_header(sheet)
    rows_num = gs.get_sheet_rows_num(sheet)
    gs.write_pls_report(db, today_pls, rows_num, sheet)
