from rasa_core_sdk import Action
from pymongo import MongoClient, DESCENDING
from .constants import TELEGRAM_DB_URI, TELEGRAM_TOKEN
import telegram


class ActionUltimas(Action):
    def name(self):
        return "action_ultimas"

    def run(self, dispatcher, tracker, domain):
        try:
            tracker_state = tracker.current_state()
            sender_id = tracker_state["sender_id"]
            message = tracker.latest_message.get("text")

            client = MongoClient(TELEGRAM_DB_URI)
            db = client["bot"]
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            projects = self.get_all_projects(db, int(message[-1]))
            for project in projects:
                message = (
                    "*{data}*\n"
                    "[{sigla} {numero}/{ano}]({url_pl})\n"
                    "_Ementa_: {ementa}\n"
                    "_Tramitação_: {tramitacao}".format(
                        data=project["data"],
                        sigla=project["sigla"],
                        numero=str(project["numero"]),
                        ano=str(project["ano"]),
                        url_pl=project["urlPL"],
                        ementa=project["ementa"],
                        tramitacao=project["tramitacao"],
                    )
                )
                bot.send_message(
                    chat_id=sender_id,
                    text=message,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
        except ValueError:
            dispatcher.utter_message(ValueError)
        return []

    def get_all_projects(self, db, number_of_projects):
        projects_to_send = []
        project_collection = db["Project"]
        projects = project_collection.find({})\
                                     .sort("data",
                                           DESCENDING)
        for i, project in enumerate(projects, start=1):
            if i <= number_of_projects:
                projects_to_send.append(project)
        return projects_to_send
