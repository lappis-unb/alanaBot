import sys
sys.path.append('../')
from tasks.celeryapp import app  # noqa: E402
from projeto.camara_concreto import ProjetoCamara  # noqa: E402
from projeto.senado_concreto import ProjetoSenado  # noqa: E402
import constants  # noqa: E402
from gsheet_report import GoogleSheetsReport  # noqa: E402
from google_forms import GoogleForms  # noqa: E402
import send_notification as notification  # noqa: E402


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
    sheet = gs.connect_sheet()
    ongs = gs.get_column_values(sheet, 1)
    palavras_chaves = gs.get_column_values(sheet, 2)
    palavras_formatadas = gs.format_palavras_chaves(ongs, palavras_chaves)
    gs.save_palavras_chaves(palavras_formatadas)


@app.task
def send_notification():
    registered_users = notification.get_registered_users()
    yesterday_pls = notification.get_yesterday_pls()
    notification.send_notification(registered_users, yesterday_pls)
