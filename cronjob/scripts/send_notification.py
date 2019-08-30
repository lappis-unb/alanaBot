# -*- coding: utf-8 -*-
from pymongo import MongoClient
import os
import logging
import telegram
import datetime


def connect_to_db():
    TELEGRAM_DB_URI = os.getenv("TELEGRAM_DB_URI","")
    client = MongoClient(TELEGRAM_DB_URI)
    db = client["bot"]
    return db

def get_registered_users(db):
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN","")
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    users = db["User"]
    query = { "registered": True }
    registered_users = users.find(query)
    return registered_users

def get_todays_pls(db):
    today = datetime.date.today().strftime("%d/%m/%Y")
    projects = db["Project"]
    query = { "data": today }
    today_pls = projects.find(query)
    pls_list = []
    for pl in today_pls:
        pls_list.append(pl)
    return pls_list

def send_notification(registered_users, pls):
    bot = telegram.Bot(token=os.getenv("TELEGRAM_TOKEN",""))
    for user in registered_users:
        for i, _ in enumerate(pls):
            bot.send_message(chat_id=user["sender_id"],
                             text="Enviando notificação sobre pls")
            message = "*{data}*\n"\
                      "[{sigla} {numero}/{ano}]({url_pl})\n"\
                      "_Ementa_: {ementa}\n"\
                      "_Tramitação_: {tramitacao}"\
                      .format(data=pls[i]["data"], sigla=pls[i]["sigla"],
                              numero=str(pls[i]["numero"]), ano=str(pls[i]["ano"]),
                              url_pl=pls[i]["urlPL"], ementa=pls[i]["ementa"],
                              tramitacao=pls[i]["tramitacao"])
            bot.send_message(chat_id=user["sender_id"], text=message,
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             disable_web_page_preview=True)


if __name__ == "__main__":
    db = connect_to_db()
    registered_users = get_registered_users(db)
    today_pls = get_todays_pls(db)
    send_notification(registered_users, today_pls)

