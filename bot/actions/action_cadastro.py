from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from pymongo import MongoClient
from .constants import TELEGRAM_DB_URI, TELEGRAM_TOKEN
import sys
import logging
import telegram


class ActionCadastro(Action):
	def name(self):
		return "action_cadastro"

	def run(self, dispatcher, tracker, domain):
		try:
			tracker_state = tracker.current_state()
			sender_id = tracker_state["sender_id"]
			client = MongoClient(TELEGRAM_DB_URI)
			db = client["bot"]
			user_data = {
				"sender_id": sender_id
			}
			self.register_telegram_user(user_data, db)
			dispatcher.utter_message("A partir de agora você vai receber "
									 "notificações regulares com as últimas "
									 "tramitações.")
		except ValueError:
			dispatcher.utter_message(ValueError)
		return []

	def build_user_data(self, sender_id):
		bot = telegram.Bot(TELEGRAM_TOKEN)
		telegram_data = bot.get_chat(sender_id)
		user_data = {
			"sender_id": sender_id,
			"first_name": telegram_data['first_name'],
			"username": telegram_data['username'],
			"registered": True
		}
		return user_data

	def register_telegram_user(self, user_data, db):
		users = db["User"]
		query = { "sender_id": user_data["sender_id"] }
		user = users.find_one(query)
		if user is None:
			user_data = self.build_user_data(user_data["sender_id"])
			db.User.insert_one(user_data)
		else:
			user_id = user['_id']
			db.User.update_one({"_id": user_id},
								{"$set": {"registered": True}})
			logging.info('User registered notification in telegram database')