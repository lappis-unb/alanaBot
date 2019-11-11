from rasa_core_sdk import Action


class ActionVoltarMenu(Action):
    def name(self):
        return "action_voltar_menu"

    def run(self, dispatcher, tracker, domain):
        try:
            tracker_state = tracker.current_state()
            sender_id = tracker_state["sender_id"]
            reply_markup = self.build_button(sender_id)
            dispatcher.utter_custom_json({
                "text": "Se você deseja voltar "
                        "para o menu selecione "
                        "o botão abaixo:",
                "reply_markup": {
                    "inline_keyboard": reply_markup
                }
            })
        except Exception:
            dispatcher.utter_message(Exception)
        return []

    def build_button(self, sender_id):
        button = [{
            "text": "voltar menu",
            "callback_data": "/menu_voltar"
        }]
        reply_markup = [button]
        return reply_markup
