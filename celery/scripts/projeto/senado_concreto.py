from datetime import datetime
from datetime import date, timedelta
import sys
import re
sys.path.append('../')
from projeto.projects import Projeto  # noqa: E402
from parlamentar.parlamentar_senado import Senador  # noqa: E402
from crawler.crawl_senado import CrawlSenado  # noqa: E402
import constants  # noqa: E402
import utils  # noqa: E402


class ProjetoSenado(Projeto):
    def __init__(self):
        self.api_url = constants.URL_API_SENADO
        self.web_url = constants.URL_WEB_SENADO
        Projeto.__init__(self)
        self.campos_banco = self.get_campos_banco()

    def get_assunto(self, keywords):
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

    def get_campos_banco(self):
        # campos_banco["ongName"] = ong_name
        # campos_banco["data"] = ['data']
        # campos_banco["urlPL"] = url_pl
        # campos_banco["casa"] = casa_projeto
        # campos_banco["apensados"] = None
        campos_banco = self.campos_projeto
        campos_banco["ementa"] = ["DetalheMateria",
                                  "Materia",
                                  "DadosBasicosMateria",
                                  "EmentaMateria"]
        campos_banco["tramitacao"] = ["DetalheMateria",
                                      "Materia",
                                      "IdentificacaoMateria",
                                      "CodigoMateria"]
        campos_banco["situacao"] = ['DetalheMateria',
                                    'Materia',
                                    'SituacaoAtual',
                                    'Autuacoes',
                                    'Autuacao',
                                    'Situacao',
                                    'DescricaoSituacao']
        campos_banco["sigla"] = ['DetalheMateria',
                                 'Materia',
                                 'IdentificacaoMateria',
                                 'SiglaSubtipoMateria']
        campos_banco["numero"] = ['DetalheMateria',
                                  'Materia',
                                  'IdentificacaoMateria',
                                  'NumeroMateria']
        campos_banco["ano"] = ['DetalheMateria',
                               'Materia',
                               'IdentificacaoMateria',
                               'AnoMateria']
        return campos_banco

    def get_projetos(self, keywords):
        projetos = []
        try:
            for codigo in keywords:
                yesterday = date.today() - timedelta(days=1)
                weekday = yesterday.weekday()
                days_const = 1
                # if it's monday get friday pls
                if weekday == self.day_of_week["dom"]:
                    days_const = 3
                req = utils.get_request(
                    self.api_url + "materia/atualizadas?"
                    f"codAssuntoEspecifico={codigo}&numdias="
                    f"{self.dias_requisicao + days_const}"
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
                        pl_date_str = datetime.strftime(pl_datetime,
                                                        "%d/%m/%Y")
                        projetos.append(
                            {
                                "id": materia["IdentificacaoMateria"]
                                             ["CodigoMateria"],
                                "data": pl_date_str
                            }
                        )
                    except TypeError:
                        pl_date = (materia["AtualizacoesRecentes"]
                                          ["Atualizacao"][-1]
                                          ["DataUltimaAtualizacao"])
                        pl_datetime = (datetime.strptime(pl_date,
                                                         "%Y-%m-%d %H:%M:%S"))
                        pl_date_str = datetime.strftime(pl_datetime,
                                                        "%d/%m/%Y")
                        projetos.append(
                            {
                                "id": materia["IdentificacaoMateria"]
                                             ["CodigoMateria"],
                                "data": pl_date_str
                            }
                        )
        except KeyError:
            print("There's no pls in this date range and this topic")
            sys.exit(1)
        else:
            return projetos

    def get_codigo_pl_arquivado(self):
        """
        Returns API id that identifies pls that have already been archived

        Returns
        ---------
        str -> API id that identifies pls that have already been archived
        """
        codigos_situacoes = utils.get_request(
            constants.URL_API_SENADO + "materia/situacoes"
        ).json()
        codigo_situacao = (codigos_situacoes['ListaSituacoes']
                                            ['Situacoes']
                                            ['Situacao'])
        for item in codigo_situacao:
            if re.match('arquivada', item['Descricao'].lower()):
                codigo_arquivado = item['Codigo']
        return codigo_arquivado

    def get_dados_pl(self, json_projeto, projeto, data_projeto, ong_name):
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
        crawl = CrawlSenado()
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
            "ementa": utils.get_from_dict(
                self.campos_banco["ementa"],
                json_projeto
            ),
            "tramitacao": crawl.crawl_tramitacao(
                json_projeto["DetalheMateria"]
                            ["Materia"]
                            ["IdentificacaoMateria"]
                            ["CodigoMateria"]),
            "situacao": situacao_pl.lower().capitalize(),
            "sigla": utils.get_from_dict(
                self.campos_banco["sigla"],
                json_projeto
            ),
            "numero": utils.get_from_dict(
                self.campos_banco["numero"],
                json_projeto
            ).strip("0"),
            "ano": utils.get_from_dict(
                self.campos_banco["ano"],
                json_projeto
            ),
            "data": data_projeto,
            "urlPL": url_pl,
            "casa": "Senado"
        }
        return dados_pl

    def save_senado_project(self, projetos, keywords, ong):
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
            ementa = utils.get_from_dict(
                self.campos_banco["ementa"],
                proj_req
            )
            # ementa = (proj_req['DetalheMateria']
            #                 ['Materia']
            #                 ["DadosBasicosMateria"]
            #                 ["EmentaMateria"])
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

            situacao_arquivada = self.get_codigo_pl_arquivado()
            senador = Senador()
            if (utils.search_keyword(ementa, keywords)
                    and situacao_arquivada != codigo_situacao_pl):
                json_autor = senador.get_dados_autor(proj_req, id_projeto)
                dados_pl = self.get_dados_pl(proj_req,
                                             id_projeto,
                                             projeto['data'],
                                             ong["Name"])
                dados_relator = senador.get_dados_relator(id_projeto)
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
                el_data['keywords'] = utils.get_ementa_keyword(
                        keywords,
                        ementa
                )
                del el_data['_id']
                constants.es.index(index='projects',
                                   doc_type='project',
                                   body=el_data)
