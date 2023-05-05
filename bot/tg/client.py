import requests
from django.conf import settings
from pydantic import ValidationError

from bot.tg.schemas import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __init__(self, token=settings.BOT_TOKEN):
        self.token = token

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset=0, timeout=60):
        data = self._get(method='getUpdates', offset=offset, timeout=timeout)
        try:
            return GetUpdatesResponse(**data)
        except ValidationError:
            return GetUpdatesResponse(ok=False, result=[])

    def send_message(self, chat_id, text):
        data = self._get(method='sendMessage', chat_id=chat_id, text=text)
        return SendMessageResponse(**data)

    def _get(self, method, **params):
        url = self.get_url(method)
        response = requests.get(url, params=params)
        if not response.ok:
            raise ValueError
        return response.json()
