# -*- coding: utf-8 -*-
import json
from requests.utils import requote_uri
from requests import get
from datetime import date, timedelta
from pymongo import MongoClient
import os
import datetime


class UpdateProjetos:
    def __init__(self):
        self.JSON_PALAVRAS_CHAVES = (
            os.path.dirname(os.path.abspath(__file__)) +
            "/palavras-chaves.json"
        )
        self.URL_API_CAMARA = "https://dadosabertos.camara.leg.br/api/v2/"
        self.QTY_DAYS = 3
        self.PL_ARQUIVADO = "Arquivada"
        self.URL_PLS_CAMARA = (
            "https://www.camara.leg.br/"
            "proposicoesWeb/fichadetramitacao"
            "?idProposicao={}"
        )

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
            for j, value in enumerate(dict_palavras_chaves[i]["keywords"]):
                if j == 0:
                    proposicoes_url += "keywords=" + value
                else:
                    proposicoes_url += "&keywords=" + value
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

    def request_projeto(self, ids_projeto, palavras_chaves):
        headers = {"Content-Type": "application/json"}
        req_id = self.URL_API_CAMARA + "proposicoes/{}"
        for id_projeto in ids_projeto:
            request_str = req_id.format(id_projeto)
            req_projeto = get(request_str, headers=headers)
            json_projeto = req_projeto.json()
            descricao_situacao = (json_projeto["dados"]
                                              ["statusProposicao"]
                                              ["descricaoSituacao"])
            ementa = json_projeto["dados"]["ementa"]
            if descricao_situacao:  # if not None
                if (self.PL_ARQUIVADO != descricao_situacao
                   and any(palavra_chave.lower() in ementa.lower()
                           for palavra_chave in palavras_chaves)):
                    db_data = self.build_projeto_dict(json_projeto)
                    db = self.connect_to_db()
                    self.save_projeto_to_db(db_data, db)

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

    def save_projeto_to_db(self, db_data, db):
        db.Project.insert_one(db_data)

    def build_projeto_dict(self, json_projeto):
        pl_date = datetime.datetime.strptime(
            json_projeto["dados"]
                        ["statusProposicao"]
                        ["dataHora"], "%Y-%m-%dT%H:%M"
        ).strftime("%d/%m/%Y")
        url_camara = (self.URL_PLS_CAMARA.format(
                      str(json_projeto["dados"]["id"])))
        db_data = {
            "ementa": json_projeto["dados"]["ementa"],
            "tramitacao": (json_projeto["dados"]
                                       ["statusProposicao"]
                                       ["despacho"]),
            "sigla": json_projeto["dados"]["siglaTipo"],
            "numero": json_projeto["dados"]["numero"],
            "ano": json_projeto["dados"]["ano"],
            "data": pl_date,
            "urlPL": url_camara,
        }
        return db_data


if __name__ == "__main__":
    TELEGRAM_DB_URI = os.getenv("TELEGRAM_DB_URI", "")
    p = UpdateProjetos()
    palavras_chaves = p.fetch_palavras_chaves()
    # print('#'*30, file=sys.stderr)
    # print(palavras_chaves, file=sys.stderr)
    # print('#'*30, file=sys.stderr)
    lista = p.fetch_projetos(palavras_chaves)
    palavras = p.fetch_palavras(palavras_chaves)
    p.request_projeto(lista, palavras)
