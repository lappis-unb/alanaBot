from rasa_core_sdk import Action
import logging


class ActionMenu(Action):
    def name(self):
        return "action_menu"

    def run(self, dispatcher, tracker, domain):
        try:
            tracker_state = tracker.current_state()
            intent = tracker.latest_message['intent'].get('name')
            sender_id = tracker_state["sender_id"]
            reply_markup = self.build_menu(sender_id)
            logging.info('#'*30)
            logging.info(reply_markup)
            logging.info('#'*30)
            if intent == 'ajuda':
                dispatcher.utter_custom_json({
                    "text": "Como posso te ajudar?",
                    "reply_markup": {"inline_keyboard": reply_markup}
                })
            else:
                dispatcher.utter_custom_json({
                    "text": "O que você deseja?",
                    "reply_markup": {"inline_keyboard": reply_markup}
                })
        except Exception:
            dispatcher.utter_message(Exception)
        return []

    def build_menu(self, sender_id):
        buttons = []
        commands = ['#cadastrar', '#descadastrar',
                    '#sobrenos', '#novidades', '#sugestao']
        for cmd in commands:
            if cmd == '#sobrenos':
                buttons.append({
                    "text": "sobre nos",
                    "callback_data": cmd
                })
            else:
                buttons.append({
                    "text":  cmd.replace('#', ''),
                    "callback_data": cmd
                })

        reply_markup = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
        return reply_markup
