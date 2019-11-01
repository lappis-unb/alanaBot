import constants
import utils
import re
from datetime import datetime
import sys


def get_assunto(keywords):
    codigos_assuntos = []
    assunto_json = utils.get_request(
                    constants.URL_API_SENADO + "materia/assuntos"
                  ).json()
    for assunto in assunto_json["ListaAssuntos"]["Assuntos"]["Assunto"]:
        if utils.search_keyword(assunto["AssuntoEspecifico"],
                                keywords):
            codigos_assuntos.append(assunto["Codigo"])
    return codigos_assuntos


def get_projetos(codigos_assuntos):
    try:
        for codigo in codigos_assuntos:
            req = utils.get_request(
                constants.URL_API_SENADO + "materia/atualizadas?"
                f"codAssuntoEspecifico={codigo}&numdias={constants.QTY_DAYS}"
            ).json()
            materias = (req['ListaMateriasAtualizadas']
                        ['Materias']
                        ['Materia'])
            projetos = [materia["IdentificacaoMateria"]
                               ["CodigoMateria"] for materia in materias]
    except KeyError:
        print("There's no pls in this date range and this topic")
        sys.exit(1)
    else:
        return projetos


def get_codigo_pl_arquivado():
    codigos_situacoes = utils.get_request(
        constants.URL_API_SENADO + "materia/situacoes"
    ).json()
    for item in codigos_situacoes['ListaSituacoes']['Situacoes']['Situacao']:
        if re.match('arquivada', item['Descricao'].lower()):
            codigo_arquivado = item['Codigo']
    return codigo_arquivado


def get_dados_autor(json_projeto):
    json_autor = {
        "autor": {}
    }
    try:
        id_autor = (json_projeto['DetalheMateria']
                                ['Materia']
                                ['Autoria']
                                ['Autor'][0]
                                ['IdentificacaoParlamentar']
                                ['CodigoParlamentar'])
        url_api_senador = (constants.URL_API_SENADO +
                           f"senador/{id_autor}")
        json_autor["autor"]["id"] = id_autor
        json_autor["autor"]["urlParlamentar"] = (
            json_projeto['DetalheMateria']['Materia']
                        ['Autoria']['Autor'][0]
                        ['IdentificacaoParlamentar']
                        ['UrlPaginaParlamentar'])
        json_autor["autor"]["urlApiParlamentar"] = url_api_senador
        json_autor["autor"]["nome"] = (
            json_projeto['DetalheMateria']['Materia']
                        ['Autoria']['Autor'][0]
                        ['IdentificacaoParlamentar']
                        ['NomeParlamentar'])

        json_autor["autor"]["sexo"] = (
            json_projeto['DetalheMateria']['Materia']
                        ['Autoria']['Autor'][0]
                        ['IdentificacaoParlamentar']
                        ['SexoParlamentar'])
        json_autor["autor"]["estado"] = (
            json_projeto['DetalheMateria']['Materia']
                        ['Autoria']['Autor'][0]
                        ['IdentificacaoParlamentar']
                        ['UfParlamentar'])
        json_autor["autor"]["siglaPartido"] = (
            json_projeto['DetalheMateria']['Materia']
                        ['Autoria']['Autor'][0]
                        ['IdentificacaoParlamentar']
                        ['SiglaPartidoParlamentar'])
    except KeyError:
        try:
            id_autor = (json_projeto['DetalheMateria']
                                    ['Materia']
                                    ['Autoria']
                                    ['Autor'][0]
                                    ['CodigoParlamentar'])
            url_api_senador = (constants.URL_API_SENADO +
                               f"senador/{id_autor}")
            json_autor["autor"]["id"] = (
                json_projeto['DetalheMateria']['Materia']
                            ['Autoria']['Autor'][0]
                            ['CodigoParlamentar'])
            json_autor["autor"]["urlParlamentar"] = (
                json_projeto['DetalheMateria']['Materia']
                            ['Autoria']['Autor'][0]
                            ['UrlPaginaParlamentar'])
            json_autor["autor"]["urlApiParlamentar"] = id_autor
            json_autor["autor"]["nome"] = (
                json_projeto['DetalheMateria']['Materia']
                            ['Autoria']['Autor'][0]
                            ['IdentificacaoParlamentar']
                            ['NomeParlamentar'])
            json_autor["autor"]["sexo"] = (
                json_projeto['DetalheMateria']['Materia']
                            ['Autoria']['Autor'][0]
                            ['IdentificacaoParlamentar']
                            ['SexoParlamentar'])

            json_autor["autor"]["estado"] = (
                json_projeto['DetalheMateria']['Materia']
                            ['Autoria']['Autor'][0]
                            ['IdentificacaoParlamentar']
                            ['UfParlamentar'])
            json_autor["autor"]["siglaPartido"] = (
                json_projeto['DetalheMateria']['Materia']
                            ['Autoria']['Autor'][0]
                            ['IdentificacaoParlamentar']
                            ['SiglaPartidoParlamentar'])
        except KeyError:
            json_autor["autor"]["nome"] = (
                json_projeto['DetalheMateria']['Materia']
                            ['Autoria']['Autor'][0]
                            ['NomeAutor'])
            json_autor["autor"]["urlParlamentar"] = None
            json_autor["autor"]["sexo"] = None
            json_autor["autor"]["estado"] = None
    return json_autor


def get_dados_pl(json_projeto, projeto, ong_name):
    pl_date = json_projeto['DetalheMateria']['Metadados']['Versao']
    pl_datetime = datetime.strptime(pl_date,
                                    "%d/%m/%Y %H:%M:%S")
    pl_date_str = datetime.strftime(pl_datetime, "%d/%m/%Y")

    url_pl = (constants.URL_WEB_SENADO +
              f"web/atividade/materias/-/materia/{projeto}")
    dados_pl = {
        "ongName": ong_name,
        "ementa": json_projeto['DetalheMateria']
                              ['Materia']
                              ["DadosBasicosMateria"]
                              ["EmentaMateria"],
        # "tramitacao": 0,
        # "apreciacao": 0,


        "situacao": json_projeto['DetalheMateria']['Materia']
                                ['SituacaoAtual']['Autuacoes']
                                ['Autuacao']['Situacao']
                                ['DescricaoSituacao'].lower()
                                                     .capitalize(),
        "sigla": json_projeto['DetalheMateria']
                             ['Materia']
                             ['IdentificacaoMateria']
                             ['SiglaSubtipoMateria'],
        "numero": json_projeto['DetalheMateria']
                              ['Materia']
                              ['IdentificacaoMateria']
                              ['NumeroMateria'],
        "ano": (json_projeto['DetalheMateria']
                            ['Materia']
                            ['IdentificacaoMateria']
                            ['AnoMateria']),
        "data": pl_date_str,
        "urlPL": url_pl,
        "casa": "Senado"
        # "regime": 0,
        # "apensados": 0
    }
    return dados_pl


def build_db_data(projetos, keywords, ong):
    for projeto in projetos:
        db_data = {}
        proj_req = utils.get_request(
            constants.URL_API_SENADO +
            f"materia/{projeto}"
        ).json()
        ementa = (proj_req['DetalheMateria']
                          ['Materia']
                          ["DadosBasicosMateria"]
                          ["EmentaMateria"])
        codigo_situacao_pl = (proj_req['DetalheMateria']['Materia']
                                      ['SituacaoAtual']['Autuacoes']
                                      ['Autuacao']['Situacao']
                                      ['CodigoSituacao'])
        situacao_arquivada = get_codigo_pl_arquivado()
        if (utils.search_keyword(ementa, keywords)
                and codigo_situacao_pl != situacao_arquivada):
            json_autor = get_dados_autor(proj_req)
            dados_pl = get_dados_pl(proj_req,
                                    projeto,
                                    ong["Name"])
            db_data.update(dados_pl)
            db_data.update(json_autor)
            save_projeto_to_db(db_data)


def save_senado_projects():
    ongs = constants.DB.Ong.find({})
    projetos = []
    for ong in ongs:
        keywords = ong["Keywords"]
        codigos_assuntos = get_assunto(keywords)
        projetos = get_projetos(codigos_assuntos)
        build_db_data(projetos, keywords, ong)


def save_projeto_to_db(db_data):
    """
    Save data from pl, deputy and reporter to database

    Args
    -------
    db_data:
        dict -> all pl data
    """
    constants.DB.Project.insert_one(db_data)


if __name__ == "__main__":
    save_senado_projects()
