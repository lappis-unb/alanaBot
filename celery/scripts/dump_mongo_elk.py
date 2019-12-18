import constants
from pymongo import DESCENDING
import re
from projeto.camara_concreto import ProjetoCamara

def get_camara_projetos():
    db = constants.DB
    project_collection = db["Project"]
    projects = (project_collection.find({
                    "casa": "Câmara"
                }).sort("data", DESCENDING))
    project_list = []
    for project in projects:
        url_pl = project["urlPL"]
        proj_id_regex = re.search("[0-9\(\)]+", url_pl)
        prod_id = proj_id_regex.group(0)
        project_list.append(prod_id)
    return project_list

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
        cam_proj = ProjetoCamara()
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
                        db_data = cam_prog.build_projeto_dict(json_projeto,
                                                              ong_name)
                        el_data = db_data
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
                        constants.es.index(index='projects',
                                           doc_type='project',
                                           body=el_data)
        except TypeError:
            return


if __name__ == "__main__":
    ongs = constants.DB.Ong.find({})
    proj_camara = ProjetoCamara()
    for ong in ongs:
        keywords = ong["Keywords"]
        ids_projetos = get_camara_projetos()
        proj_camara.request_projeto(ids_projetos, keywords, ong["Name"])
