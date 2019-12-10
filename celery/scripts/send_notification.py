# -*- coding: utf-8 -*-
import os
import telegram
import datetime
import constants

day_of_week = {
    "dom": 6,
}
db = constants.DB


def get_registered_users():
    users = db["User"]
    query = {"registered": True}
    registered_users = users.find(query)
    return registered_users


def get_yesterday_pls():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    weekday = yesterday.weekday()
    if weekday == day_of_week["dom"]:  # if it's monday get friday pls
        yesterday = datetime.date.today() - datetime.timedelta(days=3)
    projects = db["Project"]
    query = {"data": yesterday.strftime("%d/%m/%Y")}
    yesterday_pls = projects.find(query)
    pls_list = []
    for pl in yesterday_pls:
        pls_list.append(pl)
    return pls_list


def send_notification(registered_users, pls):
    bot = telegram.Bot(token=os.getenv("TELEGRAM_TOKEN", ""))
    notification_msg = "Estou muito animada com as novas atualizações!\n"\
                       "Observe que uma sociedade em que o interesse da "\
                       "criança é prioridade, é um lugar melhor "\
                       "para todos :)"
    for user in registered_users:
        for i, _ in enumerate(pls):
            message = (
                "*{data}*\n"
                "[{sigla} {numero}/{ano} - {casa}]({url_pl})\n"
                "_Ementa_: {ementa}\n"
                "_Tramitação_: {tramitacao}".format(
                    data=pls[i]["data"],
                    sigla=pls[i]["sigla"],
                    numero=str(pls[i]["numero"]),
                    ano=str(pls[i]["ano"]),
                    url_pl=pls[i]["urlPL"],
                    casa=pls[i]["casa"],
                    ementa=pls[i]["ementa"],
                    tramitacao=pls[i]["tramitacao"],
                )
            )
            if i == 0:
                bot.send_message(
                    chat_id=user["sender_id"],
                    text=notification_msg
                )
            bot.send_message(
                chat_id=user["sender_id"],
                text=message,
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )


if __name__ == "__main__":
    registered_users = get_registered_users()
    yesterday_pls = get_yesterday_pls()
    send_notification(registered_users, yesterday_pls)
