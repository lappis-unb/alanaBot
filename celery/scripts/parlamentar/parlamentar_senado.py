import sys
sys.path.append('../')
from parlamentar.parlamentar import Parlamentar  # noqa: E402
import constants  # noqa: E402
import utils  # noqa: E402


class Senador(Parlamentar):
    def __init__(self):
        Parlamentar.__init__(self)
        self.campos_relator = self.get_campos_relator()
        self.campos_autor = self.get_campos_autor()

    def get_campos_relator(self):
        campos_relator = self.campos_parlamentar
        id_autor = ['RelatoriaMateria', 'Materia'
                    'RelatoriaAtual', 'Relator'
                    'IdentificacaoParlamentar', 'CodigoParlamentar']
        campos_relator["id"] = id_autor
        campos_relator["urlParlamentar"] = ['RelatoriaMateria', 'Materia',
                                            'RelatoriaAtual', 'Relator',
                                            'IdentificacaoParlamentar',
                                            'UrlPaginaParlamentar']
        campos_relator["urlApiParlamentar"] = (constants.URL_API_SENADO +
                                               f"senador/{id_autor}")
        campos_relator["nome"] = ['RelatoriaMateria', 'Materia',
                                  'RelatoriaAtual', 'Relator',
                                  'IdentificacaoParlamentar',
                                  'NomeParlamentar']
        campos_relator["sexo"] = ['RelatoriaMateria', 'Materia',
                                  'RelatoriaAtual', 'Relator',
                                  'IdentificacaoParlamentar',
                                  'SexoParlamentar']
        campos_relator["siglaPartido"] = ['RelatoriaMateria', 'Materia',
                                          'RelatoriaAtual', 'Relator',
                                          'IdentificacaoParlamentar'
                                          'SiglaPartidoParlamentar']
        campos_relator["estado"] = {
            "uf": ['RelatoriaMateria', 'Materia',
                   'RelatoriaAtual', 'Relator',
                   'IdentificacaoParlamentar',
                   'ufParlamentar']
        }
        return campos_relator

    def get_campos_autor(self):
        campos_autor = self.campos_parlamentar
        id_autor = ['DetalheMateria', 'Materia',
                    'Autoria', 'Autor', 0,
                    'IdentificacaoParlamentar',
                    'CodigoParlamentar']
        campos_autor["id"] = id_autor
        campos_autor["urlParlamentar"] = ['DetalheMateria', 'Materia',
                                          'Autoria', 'Autor', 0,
                                          'IdentificacaoParlamentar',
                                          'UrlPaginaParlamentar']
        campos_autor["urlApiParlamentar"] = (constants.URL_API_SENADO +
                                             f"senador/{id_autor}")
        campos_autor["nome"] = ['DetalheMateria', 'Materia',
                                'Autoria', 'Autor', 0,
                                'IdentificacaoParlamentar',
                                'NomeParlamentar']
        campos_autor["sexo"] = ['DetalheMateria', 'Materia',
                                'Autoria', 'Autor', 0,
                                'IdentificacaoParlamentar',
                                'SexoParlamentar']
        campos_autor["siglaPartido"] = ['DetalheMateria', 'Materia',
                                        'Autoria', 'Autor', 0,
                                        'IdentificacaoParlamentar',
                                        'SiglaPartidoParlamentar']
        campos_autor["estado"] = {
            "uf": ['DetalheMateria', 'Materia',
                   'Autoria', 'Autor', 0,
                   'IdentificacaoParlamentar',
                   'UfParlamentar']
        }
        return campos_autor

    def get_dados_relator(self, projeto):
        json_relator = {
            "relator": {}
        }
        states_coord = constants.states_coord

        req_relator = self.get_relator_field(projeto)

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

    def get_dados_autor(self, json_projeto, projeto):
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
            uf = utils.get_from_dict(
                self.campos_autor["estado"]["uf"],
                json_projeto
            )
            id_autor = utils.get_from_dict(
                self.campos_autor["id"],
                json_projeto
            )
            url_api_senador = (constants.URL_API_SENADO +
                               f"senador/{id_autor}")
            json_autor["autor"]["id"] = id_autor
            json_autor["autor"]["urlParlamentar"] = utils.get_from_dict(
                self.campos_autor["urlParlamentar"],
                json_projeto
            )
            json_autor["autor"]["urlApiParlamentar"] = url_api_senador
            json_autor["autor"]["nome"] = utils.get_from_dict(
                self.campos_autor["nome"],
                json_projeto
            )

            json_autor["autor"]["sexo"] = utils.get_from_dict(
                self.campos_autor["sexo"],
                json_projeto
            )
            json_autor["autor"]["estado"] = {
                "uf": uf,
                "coord": {
                    "lat": states_coord[uf]
                                       ["lat"],
                    "lon": states_coord[uf]
                                       ["lon"]
                }
            }
            json_autor["autor"]["siglaPartido"] = utils.get_from_dict(
                self.campos_autor["siglaPartido"],
                json_projeto
            )
        except KeyError:
            print('AHAHAHAHAHAHAHAH')
            print(json_projeto)
            print('AHAHAHAHAHAHAHAH')
            json_autor["autor"]["nome"] = utils.get_from_dict(
                ['DetalheMateria', 'Materia',
                 'Autoria', 'Autor', 0,
                 'NomeAutor'],
                json_projeto
            )
            json_autor["autor"]["urlParlamentar"] = None
            json_autor["autor"]["sexo"] = None
            json_autor["autor"]["estado"] = None
            json_autor["autor"]["siglaPartido"] = None
        return json_autor

    def get_relator_field(self, projeto):
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
                dados_relator = (req_relator['RelatoriaMateria']['Materia']
                                            ['HistoricoRelatoria']
                                            ['Relator'][0]
                                            ['IdentificacaoParlamentar'])
            except KeyError:
                return None
        return dados_relator
