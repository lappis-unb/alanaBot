from rasa_core_sdk import Action
from pymongo import MongoClient, DESCENDING
from .constants import TELEGRAM_DB_URI
from rasa_core_sdk.events import SlotSet


class ActionUltimas(Action):
    def name(self):
        return "action_ultimas"

    def run(self, dispatcher, tracker, domain):
        try:
            message = tracker.latest_message.get("text")
            tracker_state = tracker.current_state()
            sender_id = tracker_state["sender_id"]

            client = MongoClient(TELEGRAM_DB_URI)
            db = client["bot"]
            projects = self.get_all_projects(sender_id, db, int(message[-1]))
            for project in projects:
                msg = (
                    "*{data}*\n"
                    "[{sigla} {numero}/{ano} - {casa}]({url_pl})\n"
                    "_Ementa_: {ementa}\n"
                    "_Tramitação_: {tramitacao}".format(
                        data=project["data"],
                        sigla=project["sigla"],
                        numero=str(project["numero"]),
                        ano=str(project["ano"]),
                        url_pl=project["urlPL"],
                        casa=project["casa"],
                        ementa=project["ementa"],
                        tramitacao=project["tramitacao"],
                    )
                )
                dispatcher.utter_custom_json({
                    "text": msg,
                    "parse_mode": "markdown",
                    "disable_web_page_preview": "true"
                })
        except ValueError:
            dispatcher.utter_message(ValueError)
        return [SlotSet('pl_number', int(message[-1]))]

    def get_user_ong(self, sender_id, db):
        users_collection = db["User"]
        query = {"sender_id": sender_id}
        user = users_collection.find(query)
        user_ong = user[0]["ong"]
        if user_ong:
            return user_ong
        else:
            return None

    def get_all_projects(self, sender_id, db, number_of_projects):
        projects_to_send = []
        project_collection = db["Project"]
        user_ong = self.get_user_ong(sender_id, db)
        if user_ong:
            projects = (project_collection.find({
                "ongName": user_ong
            }).sort("data", DESCENDING))
        else:
            projects = project_collection.find({})\
                                        .sort("data",
                                              DESCENDING)
        for i, project in enumerate(projects, start=1):
            if i <= number_of_projects:
                projects_to_send.append(project)
        return projects_to_send
