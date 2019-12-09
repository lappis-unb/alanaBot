import sys
from requests.utils import requote_uri
import datetime
import re
sys.path.append('../')
from projeto.projects import Projeto  # noqa: E402
import utils  # noqa: E402
import constants  # noqa: E402
from parlamentar.parlamentar_camara import Deputado   # noqa: E402
from crawler.crawl_camara import CrawlCamara   # noqa: E402


class ProjetoCamara(Projeto):
    def __init__(self):
        self.api_url = constants.URL_API_CAMARA
        self.web_url = constants.SITE_CAMARA
        Projeto.__init__(self)
        self.campos_banco = self.get_campos_banco()

    def get_campos_banco(self):
        campos_banco = self.campos_projeto
        campos_banco["ongName"] = None
        campos_banco["ementa"] = ["dados", "ementa"]
        campos_banco["tramitacao"] = ["dados",
                                      "statusProposicao",
                                      "despacho"]
        campos_banco["situacao"] = ["dados",
                                    "statusProposicao",
                                    "descricaoSituacao"]
        campos_banco["sigla"] = ["dados", "siglaTipo"]
        campos_banco["numero"] = ["dados", "numero"]
        campos_banco["ano"] = ["dados", "ano"]
        campos_banco["data"] = None
        campos_banco["urlPL"] = None
        campos_banco["regime"] = ["dados", "statusProposicao",
                                  "regime"]
        campos_banco["casa"] = "Câmara"
        campos_banco["apreciacao"] = None
        campos_banco["apensados"] = None
        return campos_banco

    def ultima_pagina_requisicao(self, req_json):
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
            last_page_url = req_json["links"][page_index]["href"]
            ultima_pagina_request = re.search(r"pagina=\d",
                                              last_page_url).group(0)
            last_page = int(''.join(filter(str.isdigit,
                                           ultima_pagina_request)))

        except IndexError:
            return
        else:
            return {"request": last_page_url,
                    "page": last_page}

    def ultimo_get_requests(self, last_page, url_projeto):
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
        for i in range(1, last_page + 1):
            url_projeto = re.sub(r"pagina=\d", f"pagina={i}", url_projeto)

            requests_projetos.append(url_projeto)
        return requests_projetos

    def get_projetos(self, list_palavras_chaves):
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
        encoded_url = self.build_pls_request_url(list_palavras_chaves)

        projetos_json = utils.get_request(encoded_url).json()

        page_req = self.ultima_pagina_requisicao(projetos_json)
        try:
            last_page = page_req["page"]
            last_page_req = page_req["request"]
        except TypeError:
            return
        else:
            request_projetos = self.ultimo_get_requests(last_page,
                                                        last_page_req)
            for proj_req in request_projetos:
                get_request = utils.get_request(proj_req)
                json_projeto = get_request.json()
                for projeto in json_projeto["dados"]:
                    ids_projetos.append(projeto["id"])
            return ids_projetos

    def build_pls_request_url(self, list_palavras_chaves):
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
        request_dates = self.get_pl_request_dates()
        proposicoes_url += (
            "&dataInicio="
            + request_dates["final_date"]
            + "&dataFim="
            + request_dates["start_date"]
            + "&itens=100"
        )
        encoded_url = requote_uri(proposicoes_url)
        return encoded_url

    def get_pl_request_dates(self):
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
        start_date = datetime.date.today()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        weekday = yesterday.weekday()
        if weekday == self.day_of_week["dom"]:  # if it's monday get friday pls
            start_date = datetime.date.today() - datetime.timedelta(days=2)

        final_date = start_date - datetime.timedelta(days=self.dias_requisicao)
        start_date_str = start_date.strftime("%Y-%m-%d")
        final_date_str = final_date.strftime("%Y-%m-%d")
        return {"start_date": start_date_str, "final_date": final_date_str}

    def request_projeto(self, ids_projeto, palavras_chaves, ong_name):
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
        try:
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
                        db_data = self.build_projeto_dict(json_projeto,
                                                          ong_name)
                        el_data = db_data
                        utils.save_projeto_to_db(db_data)
                        pl_datetime = (datetime.datetime.strptime(
                                        el_data['data'],
                                        "%d/%m/%Y"))
                        el_data['data'] = datetime.datetime.strftime(
                            pl_datetime, "%Y/%m/%d"
                        )
                        el_data['tags_ementa'] = utils.get_tags_from_string(
                            ementa
                        )
                        el_data['tags_tramitacao'] = (
                            utils.get_tags_from_string(
                                db_data["tramitacao"])
                        )
                        el_data['keywords'] = utils.get_ementa_keyword(
                            palavras_chaves,
                            ementa
                        )
                        del el_data['_id']
                        constants.es.index(index='projects',
                                           doc_type='project',
                                           body=el_data)
        except TypeError:
            return

    def build_db_data(self, json_projeto, ong_name,
                      pl_date, url_camara):
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
        crawl = CrawlCamara()
        db_data = {
            "ongName": ong_name,
            "ementa": utils.get_from_dict(self.campos_banco["ementa"],
                                          json_projeto),
            "tramitacao": utils.get_from_dict(self.campos_banco["tramitacao"],
                                              json_projeto),
            "apreciacao": crawl.crawl_apreciacao(json_projeto),
            "situacao": utils.get_from_dict(self.campos_banco["situacao"],
                                            json_projeto),
            "sigla": utils.get_from_dict(self.campos_banco["sigla"],
                                         json_projeto),
            "numero": utils.get_from_dict(self.campos_banco["numero"],
                                          json_projeto),
            "ano": utils.get_from_dict(self.campos_banco["ano"],
                                       json_projeto),
            "data": pl_date,
            "urlPL": url_camara,
            "regime": utils.get_from_dict(self.campos_banco["regime"],
                                          json_projeto),
            "apensados": crawl.crawl_apensados(json_projeto),
            "casa": "Câmara"
        }
        return db_data

    def build_projeto_dict(self, json_projeto, ong_name):
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

        dep = Deputado()
        url_relator = dep.get_url_deputado(json_projeto, True)
        url_deputado = dep.get_url_deputado(json_projeto, False)
        json_fields_relator = dep.get_json_fields(True)
        json_fields_deputado = dep.get_json_fields(False)

        dados_deputado = dep.build_deputado_final(json_fields_deputado,
                                                  url_deputado)
        dados_relator = dep.build_deputado_final(json_fields_relator,
                                                 url_relator)

        db_data = self.build_db_data(json_projeto, ong_name,
                                     pl_date, url_camara)
        db_data.update(dados_deputado)
        db_data.update(dados_relator)
        return db_data
