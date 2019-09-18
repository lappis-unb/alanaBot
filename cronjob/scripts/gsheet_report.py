import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
from pymongo import MongoClient
import os
import datetime

logger = logging.getLogger(__name__)


class GoogleSheetsReport():
    def __init__(self):
        self.secret_file = 'client_secret.json'
        self.sheet_id = '1l8gWfu4-ejJ2ZfDcoLwsyMkIUzpdbC_aTrLiGDbKUn4'

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
            sheet = client.open_by_key(self.sheet_id)
        except ValueError:
            logger.error(ValueError)
        return sheet

    def get_todays_pls(self, db):
        today = datetime.date.today().strftime("%d/%m/%Y")
        projects = db["Project"]
        query = {"data": today}
        today_pls = projects.find(query)
        pls_list = []
        for pl in today_pls:
            pls_list.append(pl)
        return pls_list

    def write_sheet(self, sheet):
        worksheet = sheet.sheet1
        worksheet.update_acell('B1', 'Bingo!')


gs = GoogleSheetsReport()
sheet = gs.connect_sheet()
gs.write_sheet(sheet)
db = gs.connect_to_db()
pls = gs.get_todays_pls(db)
