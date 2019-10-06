import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
from pymongo import MongoClient
import os
import time
import datetime
# import gspread_formatting
import gspread_formatting as gs_formatting
from xlsxwriter.utility import xl_rowcol_to_cell, xl_cell_to_rowcol


logger = logging.getLogger(__name__)


class GoogleSheetsReport():
    def __init__(self, sheet_id):
        self.secret_file = (os.path.dirname(os.path.abspath(__file__))
                            + '/client_secret.json')
        self.sheet_id = sheet_id

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
        today = "02/10/2019"
        projects = db["Project"]
        query = {"data": today}
        today_pls = projects.find(query)
        pls_list = []
        for pl in today_pls:
            pls_list.append(pl)
        return pls_list

    def write_header(self, sheet, header):
        header_cells = list(header.keys())
        header_first_col = header[header_cells[0]]
        header_last_col = header[header_cells[-1]]
        if not (self.header_exists(sheet)):
            for key in header:
                cell_coord = header[key]['coord']
                sheet.update_acell(cell_coord, key)
        gs_formatting.format_cell_range(sheet, header_first_col['coord'] +
                                        ':' + header_last_col['coord'],
                                        header_first_col['formatting'])

    def header_exists(self, sheet):
        sheet_data = sheet.get_all_values()
        try:
            if len(sheet_data) == 0:
                return False
            else:
                return True
        except IndexError:
            return False

    def get_sheet_rows_num(self, sheet):
        return len(sheet.get_all_values())

    def format_hyperlink(self, url, value):
        hyperlink_str = f'=HIPERLINK("{url}";"{value}")'
        return hyperlink_str

    def check_field_exists(self, url_field, field):
        if url_field:
            return self.format_hyperlink(
                url_field,
                field
            )
        else:
            return field

    def build_result(self, today_pls, index, header):
        dict_query = dict.fromkeys(list(header.keys()), 0)
        nome_relator = self.check_field_exists(
            today_pls[index]['relator']['urlRelator'],
            today_pls[index]['relator']['nome']
        )
        nome_autor = self.check_field_exists(
            today_pls[index]['autor']['urlDeputado'],
            today_pls[index]['autor']['nome']
        )
        dict_query = {
            'Proposição': self.format_hyperlink(
                            today_pls[index]['urlPL'],
                            today_pls[index]['sigla'] + ' ' +
                            str(today_pls[index]['numero'])
                            + '/' + str(today_pls[index]['ano'])),
            'Tramitação': today_pls[index]['regime'],
            'Apreciação': today_pls[index]['apreciacao'],
            'Situação': today_pls[index]['situacao'],
            'Ementa': today_pls[index]['ementa'],
            'Autor': nome_autor,
            'Partido Autor': today_pls[index]['autor']['siglaPartido'],
            'Estado Autor': today_pls[index]['autor']['estado'],
            'Relator': nome_relator,
            'Partido Relator': today_pls[index]['relator']['siglaPartido'],
            ' Estado Relator': today_pls[index]['relator']['estado'],
            'Apensados': today_pls[index]['apensados']
        }
        return dict_query

    def write_pls_report(self, db, today_pls, rows_num,
                         sheet, template_sheet, header):
        col = 1
        for i, _ in enumerate(today_pls):
            query_results = self.build_result(today_pls, i, header)
            for key in query_results:
                sheet.update_cell(rows_num + 1 + i, col,
                                  query_results[key])
                time.sleep(2)  # sleep to avoid sheets api request limit
                col += 1
            col = 1

    def get_header_formatting(self, sheet):
        if self.header_exists(sheet):
            sheet_data = sheet.get_all_values()
            header_formatting = {}
            for i, cell in enumerate(sheet_data[0], start=1):
                cell_coordinate = xl_rowcol_to_cell(0, i - 1)
                header_formatting[cell] = {
                    'coord': cell_coordinate,
                    'formatting': gs_formatting.
                    get_effective_format(sheet, cell_coordinate)
                }
            return header_formatting
        else:
            return False

    def format_sheet(self, sheet, template_sheet):
        sheet_data = sheet.get_all_values()
        rows_num = gs.get_sheet_rows_num(sheet)
        header = sheet_data[0]
        for cell in header:
            col_formatting = self.get_col_formatting(template_sheet, cell)
            first_row = col_formatting[0]
            col_coord = xl_cell_to_rowcol(first_row)
            time.sleep(2)
            last_row = xl_rowcol_to_cell(rows_num - 1, col_coord[1])
            gs_formatting.format_cell_range(sheet,
                                            first_row + ':' + last_row,
                                            col_formatting[1])

    def conditional_format_sheet(self, sheet, template_sheet):
        sheet_data = sheet.get_all_values()
        del sheet_data[0]  # remove header
        apreciacao_list = []
        for row in sheet_data:
            apreciacao_list.append(row[2])  # apreciação column

        for row, cell in enumerate(apreciacao_list, start=1):
            coord = xl_rowcol_to_cell(row, 2)
            if 'plenário' in cell.lower():
                cell_formatting = gs_formatting.get_effective_format(sheet,
                                                                     coord)
                cell_formatting.textFormat.foregroundColor = gs_formatting.color(1, 0, 0)
                gs_formatting.format_cell_range(sheet,
                                                coord + ':' + coord,
                                                cell_formatting)

    def get_col_formatting(self, sheet, col_name):
        try:
            cell = sheet.find(col_name)  # column name
            # cell.col to get second row, not the first
            cell_coordinate = xl_rowcol_to_cell(cell.row,
                                                cell.col - 1)
            col_formatting = gs_formatting.\
                get_effective_format(sheet, cell_coordinate)
            return (cell_coordinate, col_formatting)
        except gspread.exceptions.CellNotFound as error:
            raise error


if __name__ == "__main__":
    sheet_id = os.getenv("SHEET_ID", "")
    sheet_template_id = os.getenv("SHEET_TEMPLATE_ID", "")

    template_gs = GoogleSheetsReport(os.getenv("SHEET_TEMPLATE_ID", ""))
    template_sheet = template_gs.connect_sheet()

    gs = GoogleSheetsReport(sheet_id)
    db = gs.connect_to_db()

    today_pls = gs.get_todays_pls(db)
    sheet = gs.connect_sheet()

    header = gs.get_header_formatting(template_sheet)

    gs.write_header(sheet, header)
    rows_num = gs.get_sheet_rows_num(sheet)
    gs.write_pls_report(db, today_pls, rows_num, sheet, template_sheet, header)
    gs.format_sheet(sheet, template_sheet)
    gs.conditional_format_sheet(sheet, template_sheet)