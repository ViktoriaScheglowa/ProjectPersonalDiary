import requests

from config.settings import TELEGRAM_URL, TELEGRAM_BOT_TOKEN


def send_telegram_message(message, chat_id):
    params = {"text": message, "chat_id": chat_id}
    response = requests.get(
        f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/sendMessage", params=params
    )
