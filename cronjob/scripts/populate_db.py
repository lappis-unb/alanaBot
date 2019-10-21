# -*- coding: utf-8 -*-
import json
from requests.utils import requote_uri
from requests import get
from requests.exceptions import ConnectionError
from datetime import date, timedelta
from pymongo import MongoClient
import os
import datetime
from bs4 import BeautifulSoup
import constants
import logging
import time


class UpdateProjetos:
    def __init__(self):
        self.JSON_PALAVRAS_CHAVES = (
            os.path.dirname(os.path.abspath(__file__)) +
            "/palavras-chaves.json"
        )
        self.URL_API_CAMARA = "https://dadosabertos.camara.leg.br/api/v2/"
        self.QTY_DAYS = 1
        self.PL_ARQUIVADO = "Arquivada"
        self.URL_PLS_CAMARA = (
            "https://www.camara.leg.br/"
            "proposicoesWeb/fichadetramitacao"
            "?idProposicao={}"
        )
        self.URL_AUTORES_PL = (
            "https://dadosabertos.camara.leg.br"
            "/api/v2/proposicoes/{}/autores"
        )
        self.URL_DEPUTADOS_CAMARA = (
            "https://www.camara.leg.br/deputados/{}"
        )
        self.URL_APENSADOS_CAMARA = (
            "https://www.camara.leg.br/proposicoesWeb/{}"
        )
        self.DB = constants.DB

    def fetch_palavras_chaves(self):
        json_palavras_chaves = open(self.JSON_PALAVRAS_CHAVES,
                                    encoding="utf-8")
        palavras_chaves_str = json_palavras_chaves.read()
        dict_palavras_chaves = json.loads(palavras_chaves_str)
        return dict_palavras_chaves

    def fetch_palavras(self, palavras_chaves):
        palavras = []
        for i, _ in enumerate(palavras_chaves):
            for palavra_chave in palavras_chaves[i]["keywords"]:
                palavras.append(palavra_chave)
        return palavras

    def fetch_dates(self):
        start_date = date.today()
        final_date = start_date - timedelta(days=self.QTY_DAYS)
        start_date_str = start_date.strftime("%Y-%m-%d")
        final_date_str = final_date.strftime("%Y-%m-%d")
        return {"start_date": start_date_str, "final_date": final_date_str}

    def build_request_url(self, dict_palavras_chaves):
        proposicoes_url = self.URL_API_CAMARA + "proposicoes?"
        for i, palavra_chave in enumerate(dict_palavras_chaves):
            if i == 0:
                proposicoes_url += "keywords=" + palavra_chave
            else:
                proposicoes_url += "&keywords=" + palavra_chave
        request_dates = self.fetch_dates()
        proposicoes_url += (
            "&dataInicio="
            + request_dates["final_date"]
            + "&dataFim="
            + request_dates["start_date"]
            + "&itens=100"
        )
        encoded_url = requote_uri(proposicoes_url)
        return encoded_url

    def fetch_projetos(self, dict_palavras_chaves):
        headers = {"Content-Type": "application/json"}
        ids_projetos = []
        encoded_url = self.build_request_url(dict_palavras_chaves)
        projeto_request = get(encoded_url, headers=headers)
        projetos_json = projeto_request.json()
        request_projetos = self.get_number_of_pages(projetos_json)
        for proj_req in request_projetos:
            get_request = get(proj_req, headers=headers)
            json_projeto = get_request.json()
            for projeto in json_projeto["dados"]:
                ids_projetos.append(projeto["id"])
        return ids_projetos

    def request_projeto(self, ids_projeto, palavras_chaves, ong_name):
        headers = {"Content-Type": "application/json"}
        req_id = self.URL_API_CAMARA + "proposicoes/{}"
        for id_projeto in ids_projeto:
            request_str = req_id.format(id_projeto)
            for _ in range(100):
                req_projeto = self.can_connect(request_str, headers)
                if req_projeto[0]:
                    logging.info("API is available. Continuing...")
                    break
                else:
                    logging.warning("API is unavailable. Retrying "
                                    "in 0.5 seconds")
                    time.sleep(0.5)
            json_projeto = req_projeto[1].json()
            descricao_situacao = (json_projeto["dados"]
                                              ["statusProposicao"]
                                              ["descricaoSituacao"])
            ementa = json_projeto["dados"]["ementa"]
            if descricao_situacao:  # if not None
                if (self.PL_ARQUIVADO != descricao_situacao
                   and any(palavra_chave.lower() in ementa.lower()
                           for palavra_chave in palavras_chaves)):
                    db_data = self.build_projeto_dict(json_projeto, ong_name)
                    self.save_projeto_to_db(db_data)

    def get_number_of_pages(self, req_json):
        pages = {"first": 0, "last": 0}
        requests_projetos = []
        for link_projeto in req_json["links"]:
            if link_projeto["rel"] == "first":
                splitted_url = link_projeto["href"].split("&")
                splitted_url = [item + "&" for item in splitted_url]
                pages = self.get_page_number("first", splitted_url, pages)
            elif link_projeto["rel"] == "last":
                splitted_url = link_projeto["href"].split("&")
                splitted_url = [item + "&" for item in splitted_url]
                pages = self.get_page_number("last", splitted_url, pages)
        for i in range(pages["first"], pages["last"] + 1):
            page_request = "pagina=" + str(i) + "&"
            splitted_url[-2] = page_request
            splitted_url[-1] = splitted_url[-1].replace("&", "")
            request_str = "".join(splitted_url)
            requests_projetos.append(request_str)
        return requests_projetos

    def get_page_number(self, page, splitted_url, pages):
        if page == "first":
            page_splitted = splitted_url[-2]
            page_splitted = page_splitted.split("=")
            raw_page_number = page_splitted[-1]
            page_number = ("".join(char for char in raw_page_number
                                   if char.isdigit()))
            pages["first"] = int(page_number)
        elif page == "last":
            page_splitted = splitted_url[-2]
            page_splitted = page_splitted.split("=")
            raw_page_number = page_splitted[-1]
            page_number = ("".join(char for char in raw_page_number
                                   if char.isdigit()))
            pages["last"] = int(page_number)
        return pages

    def connect_to_db(self):
        TELEGRAM_DB_URI = os.getenv("TELEGRAM_DB_URI", "")
        client = MongoClient(TELEGRAM_DB_URI)
        db = client["bot"]
        return db

    def save_projeto_to_db(self, db_data):
        self.DB.Project.insert_one(db_data)

    def build_deputado_json(self, json_projeto):
        url_autores_pl = (self.URL_AUTORES_PL.format(
                          str(json_projeto["dados"]["id"])))
        req_autores_pl = get(url_autores_pl)
        json_autores_pl = req_autores_pl.json()
        url_deputado = json_autores_pl["dados"][0]["uri"]
        if not url_deputado:
            dados_deputado = {
                "autor": {
                    "id": None,
                    "nome": json_autores_pl["dados"][0]["nome"],
                    "siglaPartido": None,
                    "estado": None,
                    "sexo": None,
                    "urlDeputado": None
                }
            }
            return dados_deputado
        else:
            req_deputado = get(url_deputado)
            json_deputado = req_deputado.json()
            dados_deputado = json_deputado["dados"]
            dados_deputado = {
                "autor": {
                    "id": dados_deputado["id"],
                    "nome": (dados_deputado["ultimoStatus"]
                                           ["nome"].lower().title()),
                    "urlApiDeputado": dados_deputado["ultimoStatus"]["uri"],
                    "urlDeputado": (self.URL_DEPUTADOS_CAMARA
                                        .format(dados_deputado['id'])),
                    "siglaPartido": (dados_deputado["ultimoStatus"]
                                                   ["siglaPartido"]),
                    "urlPartido": dados_deputado["ultimoStatus"]["uriPartido"],
                    "estado": dados_deputado["ultimoStatus"]["siglaUf"],
                    "sexo": dados_deputado["sexo"]
                }
            }
            return dados_deputado

    def build_relator_json(self, json_projeto):
        url_relator = (json_projeto["dados"]
                                   ["statusProposicao"]
                                   ["uriUltimoRelator"])
        if url_relator:
            req_deputado = get(url_relator)
            json_deputado = req_deputado.json()
            dados_deputado = json_deputado["dados"]
            dados_deputado = {
                "relator": {
                    "id": dados_deputado["id"],
                    "urlApiRelator": dados_deputado["ultimoStatus"]["uri"],
                    "urlRelator": (self.URL_DEPUTADOS_CAMARA
                                       .format(dados_deputado['id'])),
                    "nome": (dados_deputado["ultimoStatus"]
                                           ["nome"].lower().title()),
                    "siglaPartido": (dados_deputado["ultimoStatus"]
                                                   ["siglaPartido"]),
                    "urlPartido": dados_deputado["ultimoStatus"]["uriPartido"],
                    "estado": dados_deputado["ultimoStatus"]["siglaUf"],
                    "sexo": dados_deputado["sexo"]
                }
            }
            return dados_deputado
        else:
            dados_deputado = {
                "relator": {
                    "id": None,
                    "nome": None,
                    "siglaPartido": None,
                    "estado": None,
                    "sexo": None,
                    "urlRelator": None
                }
            }
            return dados_deputado

    def build_projeto_dict(self, json_projeto, ong_name):
        pl_date = datetime.datetime.strptime(
            json_projeto["dados"]
                        ["statusProposicao"]
                        ["dataHora"], "%Y-%m-%dT%H:%M"
        ).strftime("%d/%m/%Y")
        url_camara = (self.URL_PLS_CAMARA.format(
                      str(json_projeto["dados"]["id"])))
        dados_deputado = self.build_deputado_json(json_projeto)
        dados_relator = self.build_relator_json(json_projeto)
        db_data = {
            "ongName": ong_name,
            "ementa": json_projeto["dados"]["ementa"],
            "tramitacao": (json_projeto["dados"]
                                       ["statusProposicao"]
                                       ["despacho"]),
            "apreciacao": self.crawl_apreciacao(json_projeto),
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
            "apensados": self.crawl_apensados(json_projeto)
        }
        db_data.update(dados_deputado)
        db_data.update(dados_relator)
        return db_data

    def crawl_apreciacao(self, json_projeto):
        try:
            page = get(self.URL_PLS_CAMARA.format(
                    str(json_projeto["dados"]["id"])))
            soup = BeautifulSoup(page.text, 'html.parser')
            div_apreciacao = soup.find("div",
                                       {"id": "informacoesDeTramitacao"})
            paragraph_apreciacao = div_apreciacao.find('p')
            paragraph_apreciacao.strong.decompose()
            apreciacao = paragraph_apreciacao.text.strip()
        except AttributeError:
            apreciacao = None
        return apreciacao

    def crawl_apensados(self, json_projeto):
        page = get(self.URL_PLS_CAMARA.format(
                   str(json_projeto["dados"]["id"])))
        soup = BeautifulSoup(page.text, 'html.parser')
        try:
            pls_apensados = []
            div_apensada = soup.find("div", {"id": "divResumoApensados"})
            paragraph_apensada = div_apensada.find('p')
            pls_apensados.append(paragraph_apensada.find('strong').text)
        except AttributeError:
            try:
                div_apensada = soup.find("a", {"id": "lnkArvoreDeApensados"})
                new_page = get(self.URL_APENSADOS_CAMARA.format(
                            div_apensada.get('href')))
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
            # projeto não tem apensado
            return None
        else:
            return pls_apensados[0]

    def can_connect(self, request_str, headers):
        try:
            req_projeto = get(request_str, headers=headers)
        except ConnectionError:
            return False
        return True, req_projeto

    def seed_db(self):
        ongs = self.DB.Ong.find({})
        for ong in ongs:
            ids_projetos = self.fetch_projetos(ong["Keywords"])
            self.request_projeto(ids_projetos, ong["Keywords"], ong["Name"])


if __name__ == "__main__":
    TELEGRAM_DB_URI = os.getenv("TELEGRAM_DB_URI", "")
    p = UpdateProjetos()
    p.seed_db()
