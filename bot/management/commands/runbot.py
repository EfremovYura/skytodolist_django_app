from django.conf import settings
from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from goals.models import Goal, GoalCategory, BoardParticipant, Board


class Command(BaseCommand):
    help = "run bot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)

    def handle(self, *args, **kwargs):
        offset = 0

        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg):
        tg_user, created = TgUser.objects.get_or_create(chat_id=msg.chat.id)

        if created:
            self.tg_client.send_message(chat_id=msg.chat.id, text=f"[greeting], {tg_user.user}")

        if tg_user.user:
            self.handle_authorized_user(msg, tg_user)
        else:
            self.handle_unauthorized_user(msg, tg_user)

    def handle_unauthorized_user(self, msg, tg_user):
        tg_user.verification_code = tg_user.generate_verification_code()
        tg_user.save(update_fields=['verification_code'])
        self.tg_client.send_message(chat_id=msg.chat.id, text=f"[verification code] {tg_user.verification_code}")

    def handle_authorized_user(self, msg, tg_user):
        if msg.text.startswith('/'):
            self.handle_command(tg_user, msg.text)
        else:
            # Эхо-бот
            self.tg_client.send_message(chat_id=msg.chat.id, text=msg.text)

    def handle_command(self, tg_user, msg):

        command = msg.split()[0]
        user_commands = {
            "/goals": self.list_user_goals,
            "/categories": self.list_user_categories,
            "/boards": self. list_user_boards
        }

        if command not in user_commands:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text="[unknown command]")
            command = "/help"

        if command == "/help":
            self.tg_client.send_message(chat_id=tg_user.chat_id, text=f"{user_commands.keys()}")
        else:
            user_commands[command](tg_user)

    def list_user_goals(self, tg_user):
        goals = Goal.objects.select_related('user').filter(user=tg_user.user, category__is_deleted=False) \
            .exclude(status=Goal.Status.archived)

        if goals:
            resp_msg = "Ваши цели:\n" + "\n".join([f"#{goal.id} {goal.title}" for goal in goals])
        else:
            resp_msg = "Список ваших целей пуст: []"

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)

    def list_user_categories(self, tg_user):

        categories = GoalCategory.objects.filter(
            is_deleted=False,
            board__participants__user=tg_user.user,
            board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        )

        categories_list = [f'#{category.id}: {category.title}' for category in categories]

        if categories_list:
            resp_msg = 'Доступные категории:\n' + '\n'.join(categories_list)
        else:
            resp_msg = 'У вас нет доступных категорий.'

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)

    def list_user_boards(self, tg_user: TgUser):
        boards = Board.objects.filter(participants__user_id=tg_user.user_id).exclude(is_deleted=True)

        boards_list = [f'#{board.id}: {board.title}' for board in boards]
        if boards_list:
            resp_msg = 'Доступные доски:\n' + '\n'.join(boards_list)
        else:
            resp_msg = 'У вас нет доступных досок.'

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
