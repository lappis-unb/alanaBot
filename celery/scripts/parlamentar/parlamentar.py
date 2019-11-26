from abc import ABC
import sys
sys.path.append('../')
import constants  # noqa: E402
import utils  # noqa: E402


class Parlamentar(ABC):
    def __init__(self):
        self.campos_parlamentar = {
            "id": None,
            "urlParlamentar": None,
            "urlApiParlamentar": None,
            "nome": None,
            "sexo": None,
            "siglaPartido": None,
            "estado": {
                "uf": None,
                "coord": {
                    "lat": None,
                    "lon": None
                }
            }
        }

    def get_coord_from_uf(self, dict_projeto):
        states_coord = constants.states_coord
        pl_uf = utils.get_from_dict(self.campos_senador["estado"],
                                    dict_projeto)
        pl_coord = {
            "coord": {
                "lat": states_coord[pl_uf]["lat"],
                "lon": states_coord[pl_uf]["lon"]
            }
        }
        return pl_coord
