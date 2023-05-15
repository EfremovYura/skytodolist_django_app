from typing import Any

from rest_framework import generics, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient
from django.conf import settings


class VerificationCodeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TgUserSerializer

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer: Serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tg_user: TgUser = TgUser.objects.get(verification_code=serializer.validated_data['verification_code'])
        except TgUser.DoesNotExist:
            raise AuthenticationFailed

        tg_user.user = request.user
        tg_user.save()

        TgClient(settings.BOT_TOKEN).send_message(chat_id=tg_user.chat_id, text=f'[Bot verified]. \n'
                                                                                f'Hello, {tg_user.user.username}')

        return Response(TgUserSerializer(tg_user).data)
