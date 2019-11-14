import constants
from requests.utils import requote_uri
from datetime import date, timedelta
import utils
import sys
from bs4 import BeautifulSoup
import datetime


def build_pls_request_url(list_palavras_chaves):
    """
    Returns encoded url with start date, end date and keyword parameters

    Args
    -------
    list_palavras_chaves:
        list of string -> All keywords from all subjects

    Returns
    ---------
    str -> Encoded url with start date, end date and keyword parameters

    """
    proposicoes_url = constants.URL_API_CAMARA + "proposicoes?"
    for i, palavra_chave in enumerate(list_palavras_chaves):
        if i == 0:
            proposicoes_url += "keywords=" + palavra_chave
        else:
            proposicoes_url += "&keywords=" + palavra_chave
    request_dates = get_pl_request_dates()
    proposicoes_url += (
        "&dataInicio="
        + request_dates["final_date"]
        + "&dataFim="
        + request_dates["start_date"]
        + "&itens=100"
    )
    encoded_url = requote_uri(proposicoes_url)
    return encoded_url


def get_pl_request_dates():
    """
    Returns a dictionary with start and end dates for pls requests

    Returns
    -------
        dict ->
        {
            "start_date": str in "YYYY-mm-dd" format -> start date of pls
                                                        requests
            "final_date": str in "YYYY-mm-dd" format -> end date of pls
                                                        requests
        }
    """
    start_date = date.today()
    final_date = start_date - timedelta(days=constants.QTY_DAYS)
    start_date_str = start_date.strftime("%Y-%m-%d")
    final_date_str = final_date.strftime("%Y-%m-%d")
    return {"start_date": start_date_str, "final_date": final_date_str}


def get_projetos(list_palavras_chaves):
    """
    Returns a list of integers with all pls ids

    Args
    -------
    list_palavras_chaves:
        list of strings -> All keywords from all subjects

    Returns
    ---------
    list of integers -> list of integers with all pls ids
    """
    ids_projetos = []
    encoded_url = build_pls_request_url(list_palavras_chaves)

    projeto_request = utils.get_request(encoded_url)
    projetos_json = projeto_request.json()

    last_page_splitted = search_page_name_index(projetos_json)

    last_page_index = get_last_page_number(last_page_splitted)

    request_projetos = get_pls_requests(last_page_index,
                                        last_page_splitted)
    for proj_req in request_projetos:
        get_request = utils.get_request(proj_req)
        json_projeto = get_request.json()
        for projeto in json_projeto["dados"]:
            ids_projetos.append(projeto["id"])
    return ids_projetos


def search_page_name_index(req_json):
    """
    Return request string splitted with all keywords encoded

    Args
    -------
    req_json:
        dict -> json returned by specific pl request


    Returns
    --------
    list of str -> request string splitted with all keywords encoded
    """
    try:
        page_index = [i for i, d in enumerate(req_json["links"])
                      if "last" in d.values()][0]
        page_url = req_json["links"][page_index]["href"].split("&")
        page_splitted = [item + "&" for item in page_url]
    except IndexError:
        print('NÃO TEM PL')
        sys.exit(1)
    else:
        return page_splitted


def get_pls_requests(last_page_index, last_page_splitted):
    """
    Return request string splitted with all keywords encoded

    Args
    -------
    pages:
        dict -> page name, options: first or last. Indicates the
                first and last page of pl request
    req_json:
        string -> pl request string splitted


    Returns
    --------
    list of strings -> pls request with all date
                        and keyword arguments
    """
    requests_projetos = []
    for i in range(1, last_page_index + 1):
        page_request = "pagina=" + str(i) + "&"
        last_page_splitted[-2] = page_request
        last_page_splitted[-1] = last_page_splitted[-1].replace("&", "")
        request_str = "".join(last_page_splitted)
        requests_projetos.append(request_str)
    return requests_projetos


def get_last_page_number(splitted_url):
    """
    Return request string splitted with all keywords encoded

    Args
    -------
    splitted_url:
        list of strings -> pl request string splitted

    Returns
    --------
    int -> Indicates the last page of pl request
    """
    page_splitted = splitted_url[-2]
    page_splitted = page_splitted.split("=")
    raw_page_number = page_splitted[-1]
    page_number = ("".join(char for char in raw_page_number if
                           char.isdigit()))
    last_page = int(page_number)
    return last_page


def crawl_apreciacao(json_projeto):
    """
    json_projeto:
        dict -> json returned on specific pl request

    Returns
    --------
    string -> Apreciação from specific pl
    """
    try:
        proposicao = str(json_projeto["dados"]["id"])
        page_url = (constants.SITE_CAMARA +
                    "proposicoesWeb/fichadetramitacao" +
                    f"?idProposicao={proposicao}")
        page = utils.get_request(page_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        div_apreciacao = soup.find("div",
                                   {"id": "informacoesDeTramitacao"})
        paragraph_apreciacao = div_apreciacao.find('p')
        paragraph_apreciacao.strong.decompose()
        apreciacao = paragraph_apreciacao.text.strip()
    except AttributeError:
        apreciacao = None
    return apreciacao


def crawl_apensados(json_projeto):
    """
    json_projeto:
        dict -> json returned on specific pl request

    Returns
    --------
    string -> PL's apensados from specific pl
    """
    proposicao = str(json_projeto["dados"]["id"])
    page_url = (constants.SITE_CAMARA +
                "proposicoesWeb/fichadetramitacao" +
                f"?idProposicao={proposicao}")
    page = utils.get_request(page_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    try:
        pls_apensados = []
        div_apensada = soup.find("div", {"id": "divResumoApensados"})
        paragraph_apensada = div_apensada.find('p')
        pls_apensados.append(paragraph_apensada.find('strong').text)
    except AttributeError:
        try:
            div_apensada = soup.find("a", {"id": "lnkArvoreDeApensados"})
            new_page_link = (constants.SITE_CAMARA +
                             f"proposicoesWeb/{div_apensada.get('href')}")
            new_page = utils.get_request(new_page_link)
            new_soup = BeautifulSoup(new_page.text, 'html.parser')
            uls = new_soup.find("ul", {"class": "linkProposicao"})
            lis = uls.find_all('li')
            for li in lis:
                lower_li = li.span.text.lower().strip()
                if lower_li.startswith('pl'):
                    pls_apensados.append(li.span.text)
        except AttributeError:
            return None
    except IndexError:
        return None
    else:
        return pls_apensados[0]


def get_url_deputado(json_projeto, relator=False):
    """
    Returns camara api url for deputy request

    Args
    -------
    json_projeto:
        dict -> json returned on specific pl request
    relator:
        boolean -> indicates if the url to be returned
                    is from a reporter

    Returns
    --------
    string -> camara api url for deputy request
    """
    if relator:
        url_deputado = (json_projeto["dados"]
                                    ["statusProposicao"]
                                    ["uriUltimoRelator"])
    else:
        proposicao = str(json_projeto["dados"]["id"])
        url_autores_pl = (constants.URL_API_CAMARA +
                          f"proposicoes/{proposicao}/autores")
        req_autores_pl = utils.get_request(url_autores_pl)
        json_autores_pl = req_autores_pl.json()
        url_deputado = json_autores_pl["dados"][0]["uri"]
    return url_deputado


def get_json_fields(relator=False):
    """
    Returns database fields from reporter or deputy

    Args
    -------
    relator:
        boolean -> indicates if the url to be returned
                    is from a reporter

    Returns
    --------
    dict -> database fields fom reporter or deputy
    """
    json_fields = {
        "deputado": "autor",
        "urlApi": "urlApiParlamentar",
        "urlParlamentar": "urlParlamentar"
    }
    if relator:
        json_fields = {
            "deputado": "relator",
            "urlApi": "urlApiParlamentar",
            "urlParlamentar": "urlParlamentar"
        }
    return json_fields


def build_deputado_final(json_fields, url_deputado):
    """
    Returns database fields from reporter or deputy

    Args
    -------
    json_fields:
        dict -> database fields fom reporter or deputy
    url_deputado:
        string -> camara api url for deputy request

    Returns
    --------
    dict -> all deputy data
    """
    states_coord = constants.states_coord
    if url_deputado:
        req_deputado = utils.get_request(url_deputado)
        json_deputado = req_deputado.json()
        dados_deputado = json_deputado["dados"]
        uf = dados_deputado["ultimoStatus"]["siglaUf"]
        dados_deputado = {
            json_fields["deputado"]: {
                "id": dados_deputado["id"],
                "nome": (dados_deputado["ultimoStatus"]
                                    ["nome"].lower().title()),
                json_fields["urlApi"]: (dados_deputado["ultimoStatus"]
                                                      ["uri"]),
                json_fields["urlParlamentar"]: (constants.SITE_CAMARA +
                                                "deputados/"
                                                f"{dados_deputado['id']}"),
                "siglaPartido": dados_deputado["ultimoStatus"]["siglaPartido"],
                "urlPartido": dados_deputado["ultimoStatus"]["uriPartido"],
                "estado": {
                    "uf": uf,
                    "coord": {
                        "lat": states_coord[uf]["lat"],
                        "lon": states_coord[uf]["lon"]
                    }
                },
                "sexo": dados_deputado["sexo"]
            }
        }
    else:
        dados_deputado = {
            json_fields["deputado"]: {
                "id": None,
                "nome": None,
                "siglaPartido": None,
                "estado": None,
                "sexo": None,
                json_fields["urlParlamentar"]: None
            }
        }
    return dados_deputado


def build_db_data(json_projeto, ong_name, pl_date,
                  url_camara):
    """
    Returns database fields from reporter or deputy

    Args
    -------
    json_projeto:
        dict -> json returned on specific pl request
    ong_name:
        str -> Ong name
    pl_date:
        string -> pl date in "dd/mm/YYYY" format
    url_deputado:
        string -> camara api url for deputy request
    url_camara:
        string -> camara api url for pl request

    Returns
    --------
    dict -> all pl data
    """
    db_data = {
        "ongName": ong_name,
        "ementa": json_projeto["dados"]["ementa"],
        "tramitacao": (json_projeto["dados"]
                                   ["statusProposicao"]
                                   ["despacho"]),
        "apreciacao": crawl_apreciacao(json_projeto),
        "situacao": (json_projeto["dados"]
                                 ["statusProposicao"]
                                 ["despacho"]),
        "sigla": json_projeto["dados"]["siglaTipo"],
        "numero": json_projeto["dados"]["numero"],
        "ano": json_projeto["dados"]["ano"],
        "data": pl_date,
        "urlPL": url_camara,
        "regime": (json_projeto["dados"]
                               ["statusProposicao"]
                               ["regime"]),
        "apensados": crawl_apensados(json_projeto),
        "casa": "Câmara"
    }
    return db_data


def build_projeto_dict(json_projeto, ong_name):
    """
    json_projeto:
        dict -> json returned on specific pl request
    ong_name:
        str -> Ong name

    Returns
    --------
    dict -> all data from pl, deputy and reporter
    """
    pl_date = datetime.datetime.strptime(
        json_projeto["dados"]
                    ["statusProposicao"]
                    ["dataHora"], "%Y-%m-%dT%H:%M"
    ).strftime("%d/%m/%Y")
    proposicao = str(json_projeto["dados"]["id"])
    url_camara = (constants.SITE_CAMARA +
                  "proposicoesWeb/fichadetramitacao" +
                  f"?idProposicao={proposicao}")

    url_relator = get_url_deputado(json_projeto, True)
    url_deputado = get_url_deputado(json_projeto, False)
    json_fields_relator = get_json_fields(True)
    json_fields_deputado = get_json_fields(False)

    dados_deputado = build_deputado_final(json_fields_deputado,
                                          url_deputado)
    dados_relator = build_deputado_final(json_fields_relator,
                                         url_relator)

    db_data = build_db_data(json_projeto, ong_name,
                            pl_date, url_camara)
    db_data.update(dados_deputado)
    db_data.update(dados_relator)
    return db_data


def request_projeto(ids_projeto, palavras_chaves, ong_name):
    """
    Make pls requests and save them to database

    Args
    -------
    ids_projeto:
        list of integers -> list of integers with all pls ids
    palavras_chaves:
        list of strings -> All keywords from all subjects
    ong_name:
        str -> Ong name
    """
    req_id = constants.URL_API_CAMARA + "proposicoes/{}"
    for id_projeto in ids_projeto:
        request_str = req_id.format(id_projeto)
        req_projeto = utils.get_request(request_str)
        json_projeto = req_projeto.json()
        descricao_situacao = (json_projeto["dados"]
                                          ["statusProposicao"]
                                          ["descricaoSituacao"])
        ementa = json_projeto["dados"]["ementa"]
        if descricao_situacao:  # if not None
            if (constants.PL_ARQUIVADO != descricao_situacao
                    and utils.search_keyword(ementa, palavras_chaves)):
                db_data = build_projeto_dict(json_projeto,
                                             ong_name)
                el_data = db_data
                utils.save_projeto_to_db(db_data)
                pl_datetime = (datetime.datetime.strptime(
                                el_data['data'],
                                "%d/%m/%Y"))
                el_data['data'] = datetime.datetime.strftime(
                    pl_datetime, "%Y/%m/%d"
                )
                el_data['tags_ementa'] = utils.get_tags_from_string(ementa)
                el_data['tags_tramitacao'] = utils.get_tags_from_string(
                    db_data["tramitacao"]
                )
                del el_data['_id']
                constants.es.index(index='projects',
                                   doc_type='project',
                                   body=el_data)
