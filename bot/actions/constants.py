import os

TELEGRAM_DB_URI = os.getenv('TELEGRAM_DB_URI', '')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
