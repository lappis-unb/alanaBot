import constants
import utils
import re
from datetime import datetime
import sys
from bs4 import BeautifulSoup


def get_assunto(keywords):
    """
    Returs API subject codes for keywords received by parameter

    Args
    -------
    keywords:
        list of string -> All keywords from all subjects

    Returns
    ---------
    list of string -> API subject codes for keywords received by parameter

    """
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
    """
    Returns ids of all projects that have the subject code
    received by parameter and are in the number of days
    range defined in the constants file

    Args
    -------
    codigos_assuntos:
        list of string -> API subject codes for all keywords

    Returns
    ---------
    list of strings -> Ids of all projects that have the subject code
    received by parameter and are in the number of days
    range defined in the constants file
    """
    try:
        projetos = []
        for codigo in codigos_assuntos:
            req = utils.get_request(
                constants.URL_API_SENADO + "materia/atualizadas?"
                f"codAssuntoEspecifico={codigo}&numdias="
                f"{constants.QTY_DAYS + 1}"
            ).json()
            materias = (req['ListaMateriasAtualizadas']
                        ['Materias']
                        ['Materia'])
            for materia in materias:
                try:
                    pl_date = (materia["AtualizacoesRecentes"]
                                      ["Atualizacao"]
                                      ["DataUltimaAtualizacao"])
                    pl_datetime = (datetime.strptime(pl_date,
                                                     "%Y-%m-%d %H:%M:%S"))
                    pl_date_str = datetime.strftime(pl_datetime, "%d/%m/%Y")
                    projetos.append({
                        "id": materia["IdentificacaoMateria"]
                                     ["CodigoMateria"],
                        "data": pl_date_str
                    })
                except TypeError:
                    pl_date = (materia["AtualizacoesRecentes"]
                                      ["Atualizacao"][-1]
                                      ["DataUltimaAtualizacao"])
                    pl_datetime = (datetime.strptime(pl_date,
                                                     "%Y-%m-%d %H:%M:%S"))
                    pl_date_str = datetime.strftime(pl_datetime, "%d/%m/%Y")
                    projetos.append({
                        "id": materia["IdentificacaoMateria"]
                                     ["CodigoMateria"],
                        "data": pl_date_str
                    })
    except KeyError:
        print("There's no pls in this date range and this topic")
        sys.exit(1)
    else:
        return projetos


def get_codigo_pl_arquivado():
    """
    Returns API id that identifies pls that have already been archived

    Returns
    ---------
    str -> API id that identifies pls that have already been archived
    """
    codigos_situacoes = utils.get_request(
        constants.URL_API_SENADO + "materia/situacoes"
    ).json()
    for item in codigos_situacoes['ListaSituacoes']['Situacoes']['Situacao']:
        if re.match('arquivada', item['Descricao'].lower()):
            codigo_arquivado = item['Codigo']
    return codigo_arquivado


def get_dados_autor(json_projeto, projeto):
    """
    Returns dictionary with pl author data

    Args
    -------
    json_projeto:
        dict -> json returned on specific pl request

    Returns
    --------
    dict -> all pl author data
    """
    json_autor = {
        "autor": {}
    }
    states_coord = constants.states_coord
    try:
        uf = (json_projeto['DetalheMateria']['Materia']
                          ['Autoria']['Autor'][0]
                          ['IdentificacaoParlamentar']
                          ['UfParlamentar'])
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
        json_autor["autor"]["estado"] = {
            "uf": uf,
            "coord": {
                "lat": states_coord[uf]
                                   ["lat"],
                "lon": states_coord[uf]
                                   ["lon"]
            }
        }
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
        json_autor["autor"]["siglaPartido"] = None
    return json_autor


def get_dados_relator(projeto):
    json_relator = {
        "relator": {}
    }
    states_coord = constants.states_coord

    req_relator = get_relator_field(projeto)

    if req_relator:
        dados_relator = req_relator
        id_relator = (dados_relator['CodigoParlamentar'])
        url_api_senador = (constants.URL_API_SENADO +
                           f"senador/{id_relator}")
        json_relator["relator"]["id"] = id_relator
        json_relator["relator"]["urlParlamentar"] = (
            dados_relator['UrlPaginaParlamentar']
        )
        json_relator["relator"]["urlApiParlamentar"] = url_api_senador
        json_relator["relator"]["nome"] = (
            dados_relator['NomeParlamentar'])
        json_relator["relator"]["sexo"] = (
            dados_relator['SexoParlamentar'])
        json_relator["relator"]["siglaPartido"] = (
            dados_relator['SiglaPartidoParlamentar']
        )
        json_relator["relator"]["estado"] = {
            "uf": dados_relator['UfParlamentar'],
            "coord": {
                "lat": states_coord[dados_relator['UfParlamentar']]
                                   ["lat"],
                "lon": states_coord[dados_relator['UfParlamentar']]
                                   ["lon"]
            }
        }
    else:
        json_relator["relator"] = None
    return json_relator


def get_relator_field(projeto):
    req_relator = (utils.get_request(constants.URL_API_SENADO +
                                     f"materia/relatorias/{projeto}?v=5")
                   .json())
    try:
        dados_relator = (req_relator['RelatoriaMateria']['Materia']
                                    ['RelatoriaAtual']['Relator']
                                    ['IdentificacaoParlamentar'])
    except TypeError:
        dados_relator = (req_relator['RelatoriaMateria']['Materia']
                                    ['RelatoriaAtual']['Relator'][0]
                                    ['IdentificacaoParlamentar'])
    except KeyError:
        try:
            dados_relator = (req_relator['RelatoriaMateria']['Materia']
                                        ['HistoricoRelatoria']['Relator']
                                        ['IdentificacaoParlamentar'])
        except TypeError:
            dados_relator = (dados_relator['RelatoriaMateria']['Materia']
                                          ['HistoricoRelatoria']['Relator'][0]
                                          ['IdentificacaoParlamentar'])
        except KeyError:
            return None
    return dados_relator


def get_dados_pl(json_projeto, projeto, data_projeto, ong_name):
    """
    Returns dictionary with all pl data

    Args
    -------
    json_projeto:
        dict -> json returned on specific pl request
    projeto:
        str -> PL id
    ong_name:
        str -> Ong name

    Returns
    --------
    dict -> all pl data
    """

    url_pl = (constants.URL_WEB_SENADO +
              f"web/atividade/materias/-/materia/{projeto}")
    try:
        situacao_pl = (json_projeto['DetalheMateria']['Materia']
                                   ['SituacaoAtual']['Autuacoes']
                                   ['Autuacao']['Situacao']
                                   ['DescricaoSituacao'])
    except TypeError:
        situacoes = (json_projeto['DetalheMateria']['Materia']
                                 ['SituacaoAtual']['Autuacoes'])
        situacao_pl = (situacoes['Autuacao'][0]['Situacao']
                                ['DescricaoSituacao'])
    dados_pl = {
        "ongName": ong_name,
        "ementa": json_projeto['DetalheMateria']
                              ['Materia']
                              ["DadosBasicosMateria"]
                              ["EmentaMateria"],
        "tramitacao": crawl_tramitacao(json_projeto["DetalheMateria"]
                                                   ["Materia"]
                                                   ["IdentificacaoMateria"]
                                                   ["CodigoMateria"]),
        "situacao": situacao_pl.lower().capitalize(),
        "sigla": json_projeto['DetalheMateria']
                             ['Materia']
                             ['IdentificacaoMateria']
                             ['SiglaSubtipoMateria'],
        "numero": json_projeto['DetalheMateria']
                              ['Materia']
                              ['IdentificacaoMateria']
                              ['NumeroMateria'].strip("0"),
        "ano": (json_projeto['DetalheMateria']
                            ['Materia']
                            ['IdentificacaoMateria']
                            ['AnoMateria']),
        "data": data_projeto,
        "urlPL": url_pl,
        "casa": "Senado"
    }
    return dados_pl


def save_senado_project(projetos, keywords, ong):
    """
    Saves pl from the senate in the database

    Args
    -----------
    projetos:
        list of strings -> All projects
    keywords:
        list of string -> All keywords from all subjects
    ong:
        dict -> Data from ong

    """
    for projeto in projetos:
        db_data = {}
        id_projeto = projeto['id']
        proj_req = utils.get_request(
            constants.URL_API_SENADO +
            f"materia/{id_projeto}"
        ).json()
        ementa = (proj_req['DetalheMateria']
                          ['Materia']
                          ["DadosBasicosMateria"]
                          ["EmentaMateria"])
        try:
            codigo_situacao_pl = (proj_req['DetalheMateria']['Materia']
                                          ['SituacaoAtual']['Autuacoes']
                                          ['Autuacao']['Situacao']
                                          ['CodigoSituacao'])
        except TypeError:
            situacoes = (proj_req['DetalheMateria']['Materia']
                                 ['SituacaoAtual']['Autuacoes'])
            codigo_situacao_pl = (situacoes['Autuacao'][0]['Situacao']
                                           ['CodigoSituacao'])

        situacao_arquivada = get_codigo_pl_arquivado()
        if (utils.search_keyword(ementa, keywords)
                and situacao_arquivada != codigo_situacao_pl):
            json_autor = get_dados_autor(proj_req, id_projeto)
            dados_pl = get_dados_pl(proj_req,
                                    id_projeto,
                                    projeto['data'],
                                    ong["Name"])
            dados_relator = get_dados_relator(id_projeto)
            db_data.update(dados_pl)
            db_data.update(json_autor)
            db_data.update(dados_relator)
            el_data = db_data
            utils.save_projeto_to_db(db_data)
            pl_datetime = (datetime.strptime(el_data['data'],
                                             "%d/%m/%Y"))
            el_data['data'] = datetime.strftime(pl_datetime, "%Y/%m/%d")
            el_data['tags_ementa'] = utils.get_tags_from_string(ementa)
            el_data['tags_tramitacao'] = utils.get_tags_from_string(
                dados_pl["tramitacao"]
            )
            del el_data['_id']
            constants.es.index(index='projects',
                               doc_type='project',
                               body=el_data)


def crawl_tramitacao(proposicao_id):
    """
    Returns Tramitação from specific pl

    Args
    -----------
    proposicao_id:
        dict -> json returned on specific pl request

    Returns
    --------
    string -> Tramitação from specific pl
    """
    try:
        page_url = (constants.URL_WEB_SENADO +
                    "web/atividade/materias/-/materia/" +
                    f"{proposicao_id}")
        page = utils.get_request(page_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        page_content = soup.find("div",
                                 {"id": "conteudoProjeto"})
        tramitacao = page_content.find("div",
                                       {"id": "tramitacao"})
        div_tramitacao = tramitacao.find_all("div",
                                             {"data-local": "COMISSOES"})[0]

        tramitacao_dls = div_tramitacao.find_all("dd")
        tramitacao_dts = div_tramitacao.find_all("dt")

        text_tramitacao_dls = [tramitacao_dl.text for tramitacao_dl in
                               tramitacao_dls]
        text_tramitacao_dts = [tramitacao_dt.text for tramitacao_dt in
                               tramitacao_dts]

        tramitacao_data = dict(zip(text_tramitacao_dts, text_tramitacao_dls))
        tramitacao = tramitacao_data['Ação:']
    except AttributeError:
        tramitacao = None
    return tramitacao


def main():
    """
    Execute all functions to populate db with senate projects
    """
    ongs = constants.DB.Ong.find({})
    projetos = []
    for ong in ongs:
        keywords = ong["Keywords"]
        codigos_assuntos = get_assunto(keywords)
        projetos = get_projetos(codigos_assuntos)
        save_senado_project(projetos, keywords, ong)


if __name__ == "__main__":
    main()
