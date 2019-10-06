from pymongo import MongoClient
import os

TELEGRAM_DB_URI = os.getenv("TELEGRAM_DB_URI", "")
CLIENT = MongoClient(TELEGRAM_DB_URI)
DB = CLIENT["bot"]
SHEET_ID = os.getenv("SHEET_ID", "")
SHEET_TEMPLATE_ID = os.getenv("SHEET_TEMPLATE_ID", "")
