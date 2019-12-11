from rasa_core_sdk import Action
from .constants import SHEET_ID, CLIENT_SECRET
import logging
# import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

logger = logging.getLogger(__name__)


class ActionPalavraChave(Action):
    def name(self):
        return "action_palavrachave"

    def run(self, dispatcher, tracker, domain):
        try:
            tracker_state = tracker.current_state()
            sender_id = tracker_state["sender_id"]
            reply_markup = self.build_menu(sender_id)
            dispatcher.utter_custom_json({
                "text": "Atualmente o bot possui essas divisões. "
                        "Selecione uma das opções abaixo para receber "
                        "seu conteúdo de acordo com uma divisão",
                "reply_markup": {"inline_keyboard": reply_markup}
            })
        except ValueError:
            dispatcher.utter_message(ValueError)
        return []

    def connect_sheet(self, name):
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        try:
            creds = ServiceAccountCredentials\
                            .from_json_keyfile_name(CLIENT_SECRET,
                                                    scope)
            client = gspread.authorize(creds)
        except ValueError:
            logger.error(ValueError)
        try:
            sheet = client.open_by_key(SHEET_ID)
            sheet = sheet.worksheet(name)
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

    def build_menu(self, sender_id):
        buttons = []
        sheet = self.connect_sheet("Respostas ao formulário 1")
        ongs = self.get_column_values(sheet, 1)
        for ong in ongs:
            buttons.append({
                "text":  ong,
                "callback_data": '#ong ' + ong
            })
        reply_markup = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
        return reply_markup
