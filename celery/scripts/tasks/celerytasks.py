import telegram
import sys
import os
import datetime
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
    sheet = gs.connect_sheet("Cadastro de palavras chaves")
    ongs = gs.get_column_values(sheet, 1)
    palavras_chaves = gs.get_column_values(sheet, 2)
    palavras_formatadas = gs.format_palavras_chaves(ongs, palavras_chaves)
    gs.save_palavras_chaves(palavras_formatadas)


@app.task
def send_notification():
    yesterday_pls = notification.get_yesterday_pls()
    notification.send_notification(yesterday_pls)


@app.task
def newsletter_notification():
    gs = GoogleForms(constants.SHEET_ID)
    sheet = gs.connect_sheet("Cadastro de newsletter")
    ongs = gs.get_column_values(sheet, 2)
    msgs = gs.get_column_values(sheet, 1)
    notification_dates = gs.get_column_values(sheet, 3)
    db = constants.DB
    msgs_index = []
    today = datetime.datetime.today()
    str_today = datetime.datetime.strftime(today, "%d/%m/%Y")
    for i in range(len(ongs)):
        users = db["User"]
        query = {"registered": True, "ong": ongs[i]}
        if users.count_documents(query):
            registered_users = users.find(query)
            msgs_index.append(i)
    try:
        for i, user in enumerate(registered_users):
            if str_today == notification_dates[msgs_index[i]]:
                bot = telegram.Bot(token=os.getenv("TELEGRAM_TOKEN", ""))
                bot.send_message(
                    chat_id=user["sender_id"],
                    text=msgs[msgs_index[i]],
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
    except UnboundLocalError:
        return
