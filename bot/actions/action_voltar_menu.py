from rasa_core_sdk import Action
from .constants import TELEGRAM_TOKEN
import telegram


class ActionVoltarMenu(Action):
    def name(self):
        return "action_voltar_menu"

    def run(self, dispatcher, tracker, domain):
        try:
            tracker_state = tracker.current_state()
            sender_id = tracker_state["sender_id"]
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            reply_markup = self.build_button(sender_id)
            bot.send_message(chat_id=sender_id,
                             text="Se você deseja voltar "
                                  "para o menu selecione "
                                  "o botão abaixo:",
                             reply_markup=reply_markup)
        except Exception:
            dispatcher.utter_message(Exception)
        return []

    def build_button(self, sender_id):
        button = [(telegram.InlineKeyboardButton(
                        text='voltar menu',
                        callback_data='/menu_voltar'))]
        voltar_button = [button]
        reply_markup = telegram.InlineKeyboardMarkup(voltar_button)
        return reply_markup
