from rasa_core_sdk import Action
from pymongo import MongoClient
from .constants import TELEGRAM_DB_URI, TELEGRAM_TOKEN
import logging
import telegram


class ActionStart(Action):
    def name(self):
        return "action_start"

    def run(self, dispatcher, tracker, domain):
        try:
            tracker_state = tracker.current_state()
            sender_id = tracker_state["sender_id"]
            client = MongoClient(TELEGRAM_DB_URI)
            db = client["bot"]
            user_data = self.build_user_data(sender_id)
            self.save_telegram_user(user_data, db)
            dispatcher.utter_message("Oi, eu sou a Alana, a Assistente "
                                     "Virtual do programa Prioridade "
                                     "Absoluta. Estou aqui para te "
                                     "informar sobre as novidades "
                                     "das proposições de Leis para "
                                     "Crianças e Adolescentes. Afinal, "
                                     "cuidar das crianças e dos "
                                     "adolescentes, é cuidar de todos nós!")

            dispatcher.utter_message("Para conversar comigo basta escolher "
                                     "qual opção você prefere no momento:")

            dispatcher.utter_message("#cadastrar - Caso você deseje "
                                     "receber notificações sobre as "
                                     "novidades das Leis\n"
                                     "#descadastrar - Para deixar de "
                                     "receber as notificações\n"
                                     "#ajuda - Para entender como "
                                     "podemos interagir\n"
                                     "#ultimas - Para saber sobre "
                                     "as últimas novidades de Leis\n"
                                     "(você também pode me informar "
                                     "o número de tramitações que quer "
                                     "ver. Como neste exemplo: #ultimas 5)\n"
                                     "#sobrenos - Para conhecer um pouco "
                                     "mais sobre o nosso trabalho\n"
                                     "#sugestao - Para me dizer "
                                     "uma sugestão\n")

            dispatcher.utter_message("O que você deseja?")
        except ValueError:
            dispatcher.utter_message(ValueError)
        return []

    def build_user_data(self, sender_id):
        bot = telegram.Bot(TELEGRAM_TOKEN)
        telegram_data = bot.get_chat(sender_id)
        user_data = {
            "sender_id": sender_id,
            "first_name": telegram_data["first_name"],
            "username": telegram_data["username"],
            "registered": False,
        }
        return user_data

    def save_telegram_user(self, user_data, db):
        users = db["User"]
        query = {"sender_id": user_data["sender_id"]}
        user = users.find_one(query)
        if user is None:
            user_data = self.build_user_data(user_data["sender_id"])
            db.User.insert_one(user_data)
            logging.info("User saved in telegram database")
        else:
            logging.info("User already exists in telegram database")
