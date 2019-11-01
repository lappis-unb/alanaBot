# -*- coding: utf-8 -*-
import constants
import utils
import camara_helper


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
                db_data = camara_helper.build_projeto_dict(json_projeto,
                                                           ong_name)
                save_projeto_to_db(db_data)


def save_projeto_to_db(db_data):
    """
    Save data from pl, deputy and reporter to database

    Args
    -------
    db_data:
        dict -> all pl data
    """
    constants.DB.Project.insert_one(db_data)


def seed_db():
    """
    Save data from pl, deputy and reporter to database
    """
    ongs = constants.DB.Ong.find({})
    for ong in ongs:
        ids_projetos = camara_helper.get_projetos(ong["Keywords"])
        request_projeto(ids_projetos, ong["Keywords"], ong["Name"])


if __name__ == "__main__":
    seed_db()
