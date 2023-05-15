import logging
from typing import Any

import requests
from psycopg2.extensions import JSON

from pydantic.error_wrappers import ValidationError
from requests.models import Response

from bot.tg.schemas import GetUpdatesResponse, SendMessageResponse


logger = logging.getLogger(__name__)


class TgClient:
    def __init__(self, token: str):
        self.token: str = token

    def get_url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        data = self._get(method='getUpdates', offset=offset, timeout=timeout)
        try:
            return GetUpdatesResponse(**data)
        except ValidationError:
            logger.warning(data)
            return GetUpdatesResponse(ok=False, result=[])

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        data: JSON = self._get(method='sendMessage', chat_id=chat_id, text=text)
        return SendMessageResponse(**data)

    def _get(self, method: str, **params: Any) -> JSON:
        url: str = self.get_url(method)
        response: Response = requests.get(url, params=params)

        if not response.ok:
            logger.error(f'Status code: {response.status_code}. Body: {response.content}')
            raise RuntimeError

        return response.json()
