from rasa_core_sdk import Action
from pymongo import MongoClient
from .constants import TELEGRAM_DB_URI, TELEGRAM_API_URL
import requests


class ActionCadastroOng(Action):
    def name(self):
        return "action_cadastro_ong"

    def run(self, dispatcher, tracker, domain):
        try:
            tracker_state = tracker.current_state()
            sender_id = tracker_state["sender_id"]
            message = tracker.latest_message.get("text")
            ong = message.split(' ')[-1]
            client = MongoClient(TELEGRAM_DB_URI)
            db = client["bot"]
            user_data = self.build_user_data(sender_id, ong)
            self.register_telegram_user(user_data, db, ong)
            msg = "Cadastrado para receber notificações "\
                  "com conteúdo da ong " + ong
            dispatcher.utter_message(msg)
        except ValueError:
            dispatcher.utter_message(ValueError)
        return []

    def build_user_data(self, sender_id, ong):
        get_chat_url = (TELEGRAM_API_URL +
                        f"getChat?chat_id={sender_id}")
        telegram_data = requests.get(get_chat_url).json()
        user_data = {
            "sender_id": sender_id,
            "first_name": telegram_data["result"]
                                       ["first_name"],
            "username": telegram_data["result"]
                                     ["username"],
            "registered": True,
            "ong": ong
        }
        return user_data

    def register_telegram_user(self, user_data, db, ong):
        users = db["User"]
        query = {"sender_id": user_data["sender_id"]}
        user = users.find_one(query)
        if user is None:
            user_data = self.build_user_data(user_data["sender_id"], ong)
            db.User.insert_one(user_data)
        else:
            user_id = user["_id"]
            db.User.update_one({"_id": user_id},
                               {"$set": {"registered": True, "ong": ong}})
