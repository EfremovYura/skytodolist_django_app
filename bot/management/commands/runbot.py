from django.conf import settings
from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from goals.models import Goal


class Command(BaseCommand):
    help = "run bot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)

    def handle_authorized_user(self, msg, tg_user):
        if not msg.text:
            return

        if msg.text == "/goals":
            self.fetch_tasks(msg, tg_user)
        else:
            self.tg_client.send_message(msg.chat.id, "[unknown command]")

    def handle_unauthorized_user(self, msg, tg_user):
        tg_user.verification_code = tg_user.generate_verification_code()
        tg_user.save()
        self.tg_client.send_message(chat_id=msg.chat.id,
                                    text=f"[verification code] {tg_user.verification_code}")

    def fetch_tasks(self, msg, tg_user):
        gls = Goal.objects.filter(user=tg_user.user)
        if gls.count() > 0:
            resp_msg = [f"#{item.id} {item.title}" for item in gls]
            self.tg_client.send_message(msg.chat.id, "\n".join(resp_msg))
        else:
            self.tg_client.send_message(msg.chat.id, "[goals list is empty]")



    def handle_message(self, msg):
        tg_user, created = TgUser.objects.get_or_create(chat_id=msg.chat.id)

        if created:
            self.tg_client.send_message(msg.chat.id, "[greeting]")

        if tg_user.user:
            self.handle_authorized_user(msg, tg_user)
        else:
            self.handle_unauthorized_user(msg, tg_user)

    def handle(self, *args, **kwargs):
        offset = 0

        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                print(item.message)
                self.handle_message(item.message)
                self.tg_client.send_message(chat_id=item.message.chat.id, text=item.message.text)
