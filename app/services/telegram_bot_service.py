from venv import logger

import requests

from app.core.utils.constants import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID


class TelegramBotService:
    def __init__(self) -> None:
        self.telegram_bot_token: str = TELEGRAM_BOT_TOKEN
        self.telegram_group_id: str = TELEGRAM_GROUP_ID

    def send_telegram_message(self, text: str) -> None:
        payload: dict[str, str] = {"chat_id": self.telegram_group_id, "text": text}

        try:
            response: requests.Response = requests.post(
                f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage",
                data=payload,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error sending message to Telegram: {e}")
