from rest_framework import generics, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient


class VerificationCodeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TgUserSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tg_user = TgUser.objects.get(verification_code=serializer.validated_data['verification_code'])
        except TgUser.DoesNotExist:
            raise AuthenticationFailed

        tg_user.user = request.user
        tg_user.save()

        TgClient().send_message(chat_id=tg_user.chat_id, text='Bot verified.')

        return Response(TgUserSerializer(tg_user).data)