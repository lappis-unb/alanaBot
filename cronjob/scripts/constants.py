from pymongo import MongoClient
import os

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
QTY_DAYS = 5
URL_API_SENADO = "http://legis.senado.leg.br/dadosabertos/"
URL_WEB_SENADO = "https://www25.senado.leg.br/"
