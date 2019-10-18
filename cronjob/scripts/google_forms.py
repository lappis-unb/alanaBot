import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
import os
import time
import datetime
# import gspread_formatting
import gspread_formatting as gs_formatting
from xlsxwriter.utility import xl_rowcol_to_cell, xl_cell_to_rowcol
import constants


logger = logging.getLogger(__name__)


class GoogleForms():
    def __init__(self, sheet_id):
        self.secret_file = (os.path.dirname(os.path.abspath(__file__))
                            + '/client_secret.json')
        self.sheet_id = sheet_id
        self.DB = constants.DB
        self.day_of_week = {
            "dom": 6
        }

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
            sheet = sheet.worksheet("Respostas ao formulário 1")
        except ValueError:
            logger.error(ValueError)
        return sheet

    def get_column_values(self, sheet, column):
        sheet_data = sheet.get_all_values()
        column_values = []
        for row in sheet_data:
            column_values.append(row[column])
        del column_values[0]  # remove header
        return column_values

    def save_palavras_chaves(self, dict_palavras):
        for palavras in dict_palavras:
            query = {"Name": palavras}
            if not self.DB.Ong.count_documents(query):
                self.DB.Ong.insert_one({
                    "Name": palavras,
                    "Keywords": dict_palavras[palavras]
                })
            else:
                # document already exists
                pass

    def format_palavras_chaves(self, ongs, palavras_chaves):
        dict_palavras = dict.fromkeys(ongs, [])
        for i, ong in enumerate(ongs):
            str_palavras = ''.join(palavras_chaves[i])
            lista_palavras = str_palavras.split(',')
            palavras_formatadas = [palavra.lstrip() for palavra in lista_palavras]
            dict_palavras[ong] = palavras_formatadas
        return dict_palavras


if __name__ == "__main__":
    gs = GoogleForms(constants.SHEET_ID)
    sheet = gs.connect_sheet()
    ongs = gs.get_column_values(sheet, 1)
    palavras_chaves = gs.get_column_values(sheet, 2)
    palavras_formatadas = gs.format_palavras_chaves(ongs, palavras_chaves)
    gs.save_palavras_chaves(palavras_formatadas)
