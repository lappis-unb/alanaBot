from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from pymongo import MongoClient
from .constants import TELEGRAM_DB_URI
import sys
import logging


class ActionDescadastro(Action):
	def name(self):
		return "action_descadastro"

	def run(self, dispatcher, tracker, domain):
		try:
			tracker_state = tracker.current_state()
			sender_id = tracker_state["sender_id"]
			client = MongoClient(TELEGRAM_DB_URI)
			db = client["bot"]
			user_data = {
				"sender_id": sender_id
			}
			self.unregister_telegram_user(user_data, db)			
			dispatcher.utter_message("A partir de agora você não vai "
                                     "mais receber notificações "
                                     "automáticas desse bot.")
		except ValueError:
			dispatcher.utter_message(ValueError)
		return []

	def unregister_telegram_user(self, user_data, db):
		user = db.User.find_one(user_data)
		user_id = user['_id']
		db.User.update_one({"_id": user_id},
							{"$set": {"registered": False}})
		logging.info('User unregistered notification in telegram database')