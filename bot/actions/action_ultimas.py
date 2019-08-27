from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from pymongo import MongoClient
from .constants import TELEGRAM_DB_URI
import sys
import logging


class ActionUltimas(Action):
	def name(self):
		return "action_ultimas"

	def run(self, dispatcher, tracker, domain):
		try:
			tracker_state = tracker.current_state()
			sender_id = tracker_state["sender_id"]
			message = tracker.latest_message.get("text")

			# client = MongoClient(TELEGRAM_DB_URI)
			# db = client["bot"]
			# user_data = {
			# 	"sender_id": sender_id
			# }
			# self.unregister_telegram_user(user_data, db)
			msg = "Mensagem da action de ultimas. Ultima->" + message[-1]
			dispatcher.utter_message(msg)
		except ValueError:
			dispatcher.utter_message(ValueError)
		return []

	def get_all_projects(self, db, number_of_projects):
		projects_to_send = []
		project_collection = db["Project"]
		projects = project_collection.find({})
		for i, project in enumerate(projects, start=1):
			if i <= number_of_projects:
				projects_to_send.append(project)
		return projects_to_send