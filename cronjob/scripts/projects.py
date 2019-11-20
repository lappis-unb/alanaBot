from abc import ABC, abstractmethod
from functools import reduce
from operator import getitem
import constants


class Projeto(ABC):
    def __init__(self):
        self.campos_projeto = {
            "ongName": None,
            "ementa": None,
            "tramitacao": None,
            "situacao": None,
            "sigla": None,
            "numero": None,
            "ano": None,
            "data": None,
            "urlPL": None,
            "casa": None
        }
        self.dias_requisicao = constants.QTY_DAYS
        if (self.api_url is None and self.web_url is None
                and self.campos_banco is None):
            raise NotImplementedError('Subclasses must define api '
                                      'and web urls')

    def get_from_dict(self, key_list, dict_projeto):
        return reduce(getitem, key_list, dict_projeto)

    @abstractmethod
    def get_projetos(self, keywords):
        pass
