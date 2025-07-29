import logging
from typing import Optional

import requests

from app.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class TelegramNotifier:
    def __init__(self, token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        self.token = token
        self.chat_id = chat_id

    def send_message(self, message: str, url: Optional[str] = None):
        full_message = f"🚨 *{message}*"
        if url:
            full_message += f"\n\nСсылка: {url}"

        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": full_message,
                    "parse_mode": "Markdown",
                },
                timeout=5,
            )
            if not response.ok:
                logging.error(f"Telegram error: {response.text}")
        except Exception as e:
            logging.error(f"Telegram exception: {str(e)}")
