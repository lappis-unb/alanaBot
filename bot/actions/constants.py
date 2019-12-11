import os

TELEGRAM_DB_URI = os.getenv('TELEGRAM_DB_URI', '')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
CLIENT_SECRET = (os.path.dirname(os.path.abspath(__file__))
                 + '/../client_secret.json')
SHEET_ID = os.getenv("SHEET_ID", "")
