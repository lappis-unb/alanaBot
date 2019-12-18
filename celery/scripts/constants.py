from pymongo import MongoClient
import os
from elasticsearch import Elasticsearch

TELEGRAM_DB_URI = os.getenv("TELEGRAM_DB_URI", "")
CLIENT = MongoClient(TELEGRAM_DB_URI)
DB = CLIENT["bot"]
SHEET_ID = os.getenv("SHEET_ID", "")
SHEET_TEMPLATE_ID = os.getenv("SHEET_TEMPLATE_ID", "")
URL_API_CAMARA = "https://dadosabertos.camara.leg.br/api/v2/"
PL_ARQUIVADO = "Arquivada"
SITE_CAMARA = "https://www.camara.leg.br/"
JSON_PALAVRAS_CHAVES = (
            os.path.dirname(os.path.abspath(__file__)) +
            "/palavras-chaves.json"
        )
QTY_DAYS = 1
URL_API_SENADO = "http://legis.senado.leg.br/dadosabertos/"
URL_WEB_SENADO = "https://www25.senado.leg.br/"
notification_messages = [
    "Bom dia! Aqui estão as atualizações em projetos de "
    "lei a respeito de crianças e adolescentes.",
    "Oi! Aqui estão as atualizações dos PLs "
    "sobre crianças e adolescentes.\nLembre-se "
    "que uma sociedade em que o melhor interesse "
    "de crianças e adolescentes é prioridade, "
    "é um lugar melhor para todos e todas",
    "Cuidar de crianças e adolescentes é cuidar de todos "
    "nós!\nAqui estão as atualizações do dia :)",
    "Olá, aqui estão as atualizações do dia!\n"
    "Seguimos juntas e juntos em defesa dos "
    "direitos de crianças e adolescentes.",
    "Vamos agir em defesa de crianças e "
    "adolescentes? Esse é o momento!\n"
    "Veja as atualizações do dia:",
    "Bom dia! Crianças e adolescentes "
    "devem ser prioridade absoluta no "
    "seu dia também!\nAcompanhe as atualizações "
    "de hoje em projetos de lei sobre o tema.",
    "Olá! Defender os direitos de crianças e "
    "adolescentes é um dever de todos nós!\n"
    "Acompanhe os projetos de lei sobre o tema.",
    "Seja um ativista pela infância e "
    "adolescência!\nAqui estão as atualizações "
    "de projetos de lei sobre crianças e adolescentes.",
    "Bom dia! A hora de garantir os direitos de "
    "crianças e adolescentes é agora!\n"
    "Acompanhe as atualizações de hoje "
    "em projetos de lei sobre o tema.",
    "Oi, tudo bem por aí? Vamos garantir "
    "que esteja tudo bem com as crianças e "
    "os adolescentes também?\nAqui estão "
    "as atualizações do dia.",
    "Essas são as atualizações em projetos de lei a "
    "respeito de crianças e adolescentes.\n"
    "Observe que uma sociedade em que o interesse da "
    "criança é prioridade, é um lugar melhor "
    "para todos :)"
]
es_user = os.getenv("ELASTIC_USER")
if es_user is not None:
    es_pass = os.getenv("ELASTIC_PASS")
    es = Elasticsearch([os.getenv("ELASTICSEARCH_URL", "elasticsearch:9200")],
                    http_auth=(es_user, es_pass))
else:
    es = Elasticsearch([os.getenv("ELASTICSEARCH_URL", "elasticsearch:9200")])
states_coord = {
    "AC": {
        "lat": -8.77,
        "lon": -70.55
    },
    "AL": {
        "lat": -9.71,
        "lon": -35.73
    },
    "AM": {
        "lat": -3.07,
        "lon": -61.66
    },
    "AP": {
        "lat": 1.41,
        "lon": -51.77
    },
    "BA": {
        "lat": -12.96,
        "lon": -38.51
    },
    "CE": {
        "lat": -3.71,
        "lon": -38.54
    },
    "DF": {
        "lat": -15.83,
        "lon": -47.86
    },
    "ES": {
        "lat": -19.19,
        "lon": -40.34
    },
    "GO": {
        "lat": -16.64,
        "lon": -49.31
    },
    "MA": {
        "lat": -2.55,
        "lon": -44.30
    },
    "MT": {
        "lat": -12.64,
        "lon": -55.42
    },
    "MS": {
        "lat": -20.51,
        "lon": -54.54
    },
    "MG": {
        "lat": -18.10,
        "lon": -44.38
    },
    "PA": {
        "lat": -5.53,
        "lon": -52.29
    },
    "PB": {
        "lat": -7.06,
        "lon": -35.55
    },
    "PR": {
        "lat": -24.89,
        "lon": -51.55
    },
    "PE": {
        "lat": -8.28,
        "lon": -35.07
    },
    "PI": {
        "lat": -8.28,
        "lon": -43.68
    },
    "RJ": {
        "lat": -22.84,
        "lon": -43.15
    },
    "RN": {
        "lat": -5.22,
        "lon": -36.52
    },
    "RO": {
        "lat": -11.22,
        "lon": -62.80
    },
    "RS": {
        "lat": -30.01,
        "lon": -51.22
    },
    "RR": {
        "lat":  1.89,
        "lon": -61.22
    },
    "SC": {
        "lat": -27.33,
        "lon": -49.44
    },
    "SE": {
        "lat": -10.90,
        "lon": -37.07
    },
    "SP": {
        "lat": -23.55,
        "lon": -46.64
    },
    "TO": {
        "lat": -10.25,
        "lon": -48.25
    }
}
