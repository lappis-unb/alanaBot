import telegram
import sys
import os
from celery.schedules import crontab
# from celery import add_periodic_task
import logging
sys.path.append('../')
from tasks.celeryapp import app  # noqa: E402
from projeto.camara_concreto import ProjetoCamara  # noqa: E402
from projeto.senado_concreto import ProjetoSenado  # noqa: E402
import constants  # noqa: E402
from gsheet_report import GoogleSheetsReport  # noqa: E402
from google_forms import GoogleForms  # noqa: E402
import send_notification as notification  # noqa: E402

logger = logging.getLogger(__name__)

day_of_week = {
    "Segunda-feira": "mon",
    "Terça-feira": "tue",
    "Quarta-feira": "wed",
    "Quinta-feira": "thu",
    "Sexta-feira": "fri"
}
current_module = __import__(__name__)


@app.task
def seed_db():
    """
    Save data from pl, deputy and reporter to database
    """
    ongs = constants.DB.Ong.find({})
    proj_camara = ProjetoCamara()
    proj_senado = ProjetoSenado()
    for ong in ongs:
        keywords = ong["Keywords"]
        ids_projetos = proj_camara.get_projetos(keywords)
        proj_camara.request_projeto(ids_projetos, keywords, ong["Name"])

        codigos_assuntos_senado = proj_senado.get_assunto(keywords)
        projetos_senado = proj_senado.get_projetos(codigos_assuntos_senado)
        proj_senado.save_senado_project(projetos_senado, keywords, ong)


@app.task
def seed_gsheet_report():
    template_gs = GoogleSheetsReport(constants.SHEET_TEMPLATE_ID)
    template_sheet = template_gs.connect_sheet()
    gs = GoogleSheetsReport(constants.SHEET_ID)
    existing_pages = gs.get_existing_sheets()
    gs.update_sheets(existing_pages)
    template_header_formatting = gs.get_template_header_formatting(
        template_sheet
    )
    gs.write_sheet_report(template_sheet, template_header_formatting)


@app.task
def seed_google_forms():
    gs = GoogleForms(constants.SHEET_ID)
    sheet = gs.connect_sheet("Respostas ao formulário 1")
    ongs = gs.get_column_values(sheet, 1)
    palavras_chaves = gs.get_column_values(sheet, 2)
    palavras_formatadas = gs.format_palavras_chaves(ongs, palavras_chaves)
    gs.save_palavras_chaves(palavras_formatadas)


@app.task
def send_notification():
    registered_users = notification.get_registered_users()
    yesterday_pls = notification.get_yesterday_pls()
    notification.send_notification(registered_users, yesterday_pls)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    gs = GoogleForms(constants.SHEET_ID)
    sheet = gs.connect_sheet("Respostas ao formulário 4")
    scheduled_hour = gs.get_column_values(sheet, 3)
    notification_freq = gs.get_column_values(sheet, 4)
    notification_days = gs.get_column_values(sheet, 5)
    msgs = gs.get_column_values(sheet, 1)

    for i in range(len(scheduled_hour)):
        notification_hour = scheduled_hour[i].split(':')
        days_of_week = 'mon,tue,'\
                       'wed,thu,'\
                       'fri'
        if notification_freq == "Semanalmente":
            notification_days_split = notification_days[i].split(',')
            splitted_days = [day.lstrip() for day in notification_days_split]
            formatted_days_list = [day_of_week[day] for day in splitted_days]
            days_of_week = ','.join(str(day) for day in formatted_days_list)
        sender.add_periodic_task(
            crontab(hour=notification_hour[0],
                    minute=notification_hour[1],
                    day_of_week=days_of_week),
            newsletter_notification.s(msgs[i])
        )


@app.task
def newsletter_notification(msg):
    gs = GoogleForms(constants.SHEET_ID)
    sheet = gs.connect_sheet("Respostas ao formulário 4")
    ongs = gs.get_column_values(sheet, 2)
    db = constants.DB
    for i in range(len(ongs)):
        users = db["User"]
        query = {"registered": True, "ong": ongs[i]}
        registered_users = users.find(query)
    for user in registered_users:
        bot = telegram.Bot(token=os.getenv("TELEGRAM_TOKEN", ""))
        bot.send_message(
            chat_id=user["sender_id"],
            text=msg,
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
