import logging

import requests

from src.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class TelegramNotifier:
    def __init__(self, token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        self.token = token
        self.chat_id = chat_id

    def send_message(self, message: str):
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                },
                timeout=5,
            )
            if not response.ok:
                logging.error(f"Telegram send_message failed: {response.text}")
        except Exception as e:
            logging.error(f"Telegram send_message exception: {str(e)}")
