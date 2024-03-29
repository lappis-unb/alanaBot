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


class GoogleSheetsReport():
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
            sheet = client.open_by_key(self.sheet_id).sheet1
        except ValueError:
            logger.error(ValueError)
        return sheet

    def get_yesterday_pls(self, ong_name):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        weekday = yesterday.weekday()
        if weekday == self.day_of_week["dom"]:  # if it's monday get friday pls
            yesterday = datetime.date.today() - datetime.timedelta(days=3)
        projects = self.DB["Project"]
        query = {"data": yesterday.strftime("%d/%m/%Y"), "ongName": ong_name}
        yesterday_pls = projects.find(query)
        pls_list = []
        for pl in yesterday_pls:
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

    def return_none_if_not_exists(self, field):
        try:
            if field:
                return field
        except TypeError:
            return None

    def build_result(self, yesterday_pls, index, header):
        dict_query = dict.fromkeys(list(header.keys()), 0)
        nome_autor = self.check_field_exists(
            yesterday_pls[index]['autor']['urlParlamentar'],
            yesterday_pls[index]['autor']['nome']
        )
        nome_relator = self.check_field_exists(
            yesterday_pls[index]['relator']['urlParlamentar'],
            yesterday_pls[index]['relator']['nome']
        )
        casa_pl = yesterday_pls[index]['casa']
        if casa_pl == 'Câmara':
            apreciacao = yesterday_pls[index]['apreciacao']
            apensados = yesterday_pls[index]['apensados']
            tramitacao = yesterday_pls[index]['regime']
        else:
            apreciacao = None
            apensados = None
            tramitacao = yesterday_pls[index]['tramitacao']
        try:
            uf_autor = (yesterday_pls[index]
                                     ['autor']
                                     ['estado']
                                     ['uf'])
        except TypeError:
            uf_autor = None
        try:
            uf_relator = (yesterday_pls[index]
                                       ['relator']
                                       ['estado']
                                       ['uf'])
        except TypeError:
            uf_relator = None
        dict_query = {
            'Proposição': self.format_hyperlink(
                            yesterday_pls[index]['urlPL'],
                            yesterday_pls[index]['sigla'] + ' ' +
                            str(yesterday_pls[index]['numero'])
                            + '/' + str(yesterday_pls[index]['ano'])
                            + f' - {casa_pl}'),
            'Tramitação': tramitacao,
            'Apreciação': apreciacao,
            'Situação': yesterday_pls[index]['situacao'],
            'Ementa': yesterday_pls[index]['ementa'],
            'Autor': nome_autor,
            'Partido Autor': (yesterday_pls[index]
                                           ['autor']
                                           ['siglaPartido']),
            'Estado Autor': uf_autor,
            'Relator': nome_relator,
            'Partido Relator': (yesterday_pls[index]
                                             ['relator']
                                             ['siglaPartido']),
            ' Estado Relator': uf_relator,
            'Apensados': apensados
        }
        return dict_query

    def write_pls_report(self, yesterday_pls, rows_num,
                         sheet, template_sheet, template_header):
        col = 1
        for i, _ in enumerate(yesterday_pls):
            query_results = self.build_result(yesterday_pls, i,
                                              template_header)
            for key in query_results:
                row, i = self.get_sheet_pls(sheet, i, yesterday_pls,
                                            template_header, rows_num)
                sheet.update_cell(row, col,
                                  query_results[key])
                time.sleep(3)  # sleep to avoid sheets api request limit
                col += 1
            col = 1

    def get_sheet_pls(self, sheet, index,
                      yesterday_pls, template_header,
                      rows_num):
        sheet_pls = self.get_column_values(sheet, 'Proposição',
                                           template_header)
        try:
            casa_pl = yesterday_pls[index]['casa']
            row = sheet_pls.index(yesterday_pls[index]['sigla'] + ' ' +
                                  str(yesterday_pls[index]['numero'])
                                  + '/' + str(yesterday_pls[index]['ano'])
                                  + f' - {casa_pl}')
            # 2 because gspread start indexing at 1 and the header row
            # was removed in the get column values method
            if not self.header_exists(sheet):
                return row + 2, index - 1
            else:
                return row + 2, index
        except ValueError:
            row = rows_num + 1 + index
            return row, index

    def get_template_header_formatting(self, template_sheet):
        if self.header_exists(template_sheet):
            sheet_data = template_sheet.get_all_values()
            template_header_formatting = {}
            for template_sheet_col, cell in enumerate(sheet_data[0], start=0):
                cell_coordinate = xl_rowcol_to_cell(0, template_sheet_col)
                template_header_formatting[cell] = {
                    'coord': cell_coordinate,
                    'formatting': gs_formatting.
                    get_effective_format(template_sheet, cell_coordinate),
                    'column_index': template_sheet_col
                }
            return template_header_formatting
        else:
            return False

    def format_sheet(self, sheet, template_sheet):
        sheet_data = sheet.get_all_values()
        rows_num = self.get_sheet_rows_num(sheet)
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

    def get_column_values(self, sheet, column_name, template_header):
        sheet_data = sheet.get_all_values()
        column_values = []
        for row in sheet_data:
            column_values.append(row[template_header[column_name]
                                                    ['column_index']])
        del column_values[0]  # remove header
        return column_values

    def conditional_format_sheet(self, sheet, template_sheet, template_header):
        apreciacao_list = self.get_column_values(sheet, 'Situação',
                                                 template_header)
        for row, cell in enumerate(apreciacao_list, start=1):
            coord = xl_rowcol_to_cell(row,
                                      template_header['Situação']
                                                     ['column_index'])
            if 'pauta' in cell.lower():
                cell_formatting = gs_formatting.get_effective_format(sheet,
                                                                     coord)
                cell_formatting.textFormat.foregroundColor =\
                    gs_formatting.color(1, 0, 0)
                gs_formatting.format_cell_range(sheet,
                                                coord + ':' + coord,
                                                cell_formatting)

    def get_col_formatting(self, sheet, col_name):
        try:
            cell = sheet.find(col_name)  # column name
            cell_coordinate = xl_rowcol_to_cell(cell.row,
                                                cell.col - 1)
            col_formatting = gs_formatting.\
                get_effective_format(sheet, cell_coordinate)
            return (cell_coordinate, col_formatting)
        except gspread.exceptions.CellNotFound as error:
            raise error

    def get_existing_sheets(self):
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
            sheets = sheet.worksheets()
            existing_pages = []
            for sheet in sheets:
                existing_pages.append(sheet.title)
        except ValueError:
            logger.error(ValueError)
        return existing_pages

    def update_sheets(self, existing_pages):
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
            ongs = self.DB.Ong.find({}, {"Name": 1})
            for ong in ongs:
                if ong['Name'] not in existing_pages:
                    sheet.add_worksheet(title=ong['Name'],
                                        rows="10000",
                                        cols="26")
        except ValueError:
            logger.error(ValueError)

    def connect_sheet_by_name(self, name):
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
            sheet = sheet.worksheet(name)
        except ValueError:
            logger.error(ValueError)
        return sheet

    def write_sheet_report(self, template_sheet, template_header_formatting):
        ongs = self.DB.Ong.find({})
        for ong in ongs:
            sheet = self.connect_sheet_by_name(ong["Name"])
            yesterday_pls = self.get_yesterday_pls(ong["Name"])
            self.write_header(sheet, template_header_formatting)
            rows_num = self.get_sheet_rows_num(sheet)
            self.write_pls_report(yesterday_pls, rows_num, sheet,
                                  template_sheet, template_header_formatting)
            self.format_sheet(sheet, template_sheet)
            self.conditional_format_sheet(sheet, template_sheet,
                                          template_header_formatting)


if __name__ == "__main__":
    template_gs = GoogleSheetsReport(constants.SHEET_TEMPLATE_ID)
    template_sheet = template_gs.connect_sheet()
    gs = GoogleSheetsReport(constants.SHEET_ID)
    existing_pages = gs.get_existing_sheets()
    gs.update_sheets(existing_pages)
    template_header_formatting = gs.get_template_header_formatting(
        template_sheet
    )
    gs.write_sheet_report(template_sheet, template_header_formatting)
