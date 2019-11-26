import sys
sys.path.append('../')
from parlamentar.parlamentar import Parlamentar  # noqa: E402
import constants  # noqa: E402
import utils  # noqa: E402


class Deputado(Parlamentar):
    def __init__(self):
        Parlamentar.__init__(self)
        self.campos_deputado = self.get_campos_deputado()

    def get_coord_from_uf(self, dict_projeto):
        states_coord = constants.states_coord
        pl_uf = utils.get_from_dict(self.campos_deputado["estado"],
                                    dict_projeto)
        pl_coord = {
            "coord": {
                "lat": states_coord[pl_uf]["lat"],
                "lon": states_coord[pl_uf]["lon"]
            }
        }
        return pl_coord

    def get_campos_deputado(self):
        campos_deputado = self.campos_parlamentar
        # dados_parlamentar = ['RelatoriaMateria', 'Materia'
        #                      'RelatoriaAtual', 'Relator',
        #                      'IdentificacaoParlamentar']
        # id_parlamentar = ['RelatoriaMateria', 'Materia'
        #                   'RelatoriaAtual', 'Relator'
        #                   'IdentificacaoParlamentar', 'CodigoParlamentar']

        # dados deputado
        id_parlamentar = ["dados", "id"]
        campos_deputado["id"] = id_parlamentar

        # dados deputado
        campos_deputado["urlParlamentar"] = (constants.SITE_CAMARA +
                                             "deputados/"
                                             f"{id_parlamentar}")
        # dados deputado
        campos_deputado["urlApiParlamentar"] = ["dados", "ultimoStatus", "uri"]

        # dados deputado
        campos_deputado["nome"] = ["dados", "ultimoStatus", "nome"]

        # dados deputado
        campos_deputado["sexo"] = ['dados', 'sexo']

        # dados deputado
        campos_deputado["siglaPartido"] = ["dados", "ultimoStatus",
                                           "siglaPartido"]

        # dados deputado
        campos_deputado["urlPartido"] = ["dados", "ultimoStatus",
                                         "uriPartido"]
        campos_deputado["estado"] = {
            "uf": ["dados", "ultimoStatus", "siglaUf"]
        }
        return campos_deputado

    def get_url_deputado(self, json_projeto, relator=False):
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

    def get_json_fields(self, relator=False):
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
            "urlApiParlamentar": "urlApiParlamentar",
            "urlParlamentar": "urlParlamentar"
        }
        if relator:
            json_fields = {
                "deputado": "relator",
                "urlApiParlamentar": "urlApiParlamentar",
                "urlParlamentar": "urlParlamentar"
            }
        return json_fields

    def build_deputado_final(self, json_fields, url_deputado):
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
            uf = utils.get_from_dict(
                        self.campos_deputado["estado"]["uf"],
                        json_deputado)
            dados_deputado = {
                json_fields["deputado"]: {
                    "id": utils.get_from_dict(self.campos_deputado["id"],
                                              json_deputado),
                    "nome": utils.get_from_dict(self.campos_deputado["nome"],
                                                json_deputado).lower()
                                                              .title(),
                    json_fields["urlApiParlamentar"]: utils.get_from_dict(
                        self.campos_deputado["urlApiParlamentar"],
                        json_deputado),
                    json_fields["urlParlamentar"]: self.campos_deputado[
                        "urlParlamentar"],
                    "siglaPartido": utils.get_from_dict(
                        self.campos_deputado["siglaPartido"],
                        json_deputado),
                    "urlPartido": utils.get_from_dict(
                        self.campos_deputado["urlPartido"],
                        json_deputado),
                    "estado": {
                        "uf": uf,
                        "coord": {
                            "lat": states_coord[uf]["lat"],
                            "lon": states_coord[uf]["lon"]
                        }
                    },
                    "sexo": json_deputado["dados"]["sexo"]
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
