from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from pymongo import MongoClient
from .constants import TELEGRAM_DB_URI, TELEGRAM_TOKEN
import sys
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
			dispatcher.utter_message("Esse bot envia notificações de atualizações "
									 "nos projetos de lei que são relevantes para "
									 "a privacidade, liberdade de expressão, acesso "
									 "e questões de gênero no meio digital. A lista "
									 "completa dos projetos atualmente monitorados está "
									 "em https://codingrights.gitlab.io/pls/.")
			dispatcher.utter_message("Esta é a versão beta, logo teremos mais "
									 "funcionalidades e comandos implementados. "
									 "Se você tem sugestões, também pode entrar "
									 "em contato pelo email contact@codingrights.org")
			dispatcher.utter_message("Use os seguintes comandos para interagir com o bot:")
			dispatcher.utter_message("/cadastrar - Para passar a receber notificações.\n"
									 "/descadastrar - Para deixar de receber notificações.\n"
									 "/ajuda - Para mostrar esse texto.\n"
									 "/ultimas - Para mostrar últimas tramitações (você pode, "
									 "se quiser, informar o número de tramitações que quer ver. "
									 "Por exemplo: /ultimas 5).")
		except ValueError:
			dispatcher.utter_message(ValueError)
		return []

	def build_user_data(self, sender_id):
		bot = telegram.Bot(TELEGRAM_TOKEN)
		telegram_data = bot.get_chat(sender_id)
		user_data = {
			"sender_id": sender_id,
			"first_name": telegram_data['first_name'],
			"username": telegram_data['username']
		}
		return user_data
		

	def save_telegram_user(self, user_data, db):
		db.User.insert_one(user_data)
		logging.info('User saved in telegram database')