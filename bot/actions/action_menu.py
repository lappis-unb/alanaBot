from rasa_core_sdk import Action
from .constants import TELEGRAM_TOKEN
import telegram


class ActionMenu(Action):
    def name(self):
        return "action_menu"

    def run(self, dispatcher, tracker, domain):
        try:
            tracker_state = tracker.current_state()
            intent = tracker.latest_message['intent'].get('name')
            sender_id = tracker_state["sender_id"]
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            reply_markup = self.build_menu(sender_id)
            if intent == 'ajuda':
                bot.send_message(chat_id=sender_id,
                                 text="Como posso te ajudar?",
                                 reply_markup=reply_markup)
            else:
                bot.send_message(chat_id=sender_id,
                                 text="O que você deseja?",
                                 reply_markup=reply_markup)
        except Exception:
            dispatcher.utter_message(Exception)
        return []

    def build_menu(self, sender_id):
        buttons = []
        commands = ['#cadastrar', '#descadastrar',
                    '#sobrenos', '#novidades', '#sugestao']
        for cmd in commands:
            if cmd == '#sobrenos':
                buttons.append(telegram.InlineKeyboardButton(
                                text='sobre nos',
                                callback_data=cmd))
            else:
                buttons.append(telegram.InlineKeyboardButton(
                                text=cmd.replace('#', ''),
                                callback_data=cmd))
        cmd_menu = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
        reply_markup = telegram.InlineKeyboardMarkup(cmd_menu)
        return reply_markup
