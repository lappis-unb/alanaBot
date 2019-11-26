from celery import Celery
# from camara_concreto import ProjetoCamara
# from senado_concreto import ProjetoSenado
from projeto.camara_concreto import ProjetoCamara
from projeto.senado_concreto import ProjetoSenado
import constants

app = Celery()
app.config_from_object('celeryconfig')


@app.task
def add(x, y):
    return x + y


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
