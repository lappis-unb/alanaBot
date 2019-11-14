# -*- coding: utf-8 -*-
import constants
import camara_helper
import senado_helper


def seed_db():
    """
    Save data from pl, deputy and reporter to database
    """
    ongs = constants.DB.Ong.find({})
    for ong in ongs:
        keywords = ong["Keywords"]
        ids_projetos = camara_helper.get_projetos(keywords)
        camara_helper.request_projeto(ids_projetos, keywords, ong["Name"])

        codigos_assuntos_senado = senado_helper.get_assunto(keywords)
        projetos_senado = senado_helper.get_projetos(codigos_assuntos_senado)
        senado_helper.save_senado_project(projetos_senado, keywords, ong)


if __name__ == "__main__":
    seed_db()
