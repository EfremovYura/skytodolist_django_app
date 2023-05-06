import logging

from django.conf import settings
from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from goals.models import Goal, GoalCategory, BoardParticipant, Board
from goals.serializers import GoalSerializer, BoardSerializer, GoalCategorySerializer


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

        command, *params = msg.split()
        user_commands = {
            "/goals": self._list_user_goals,
            "/categories": self._list_user_categories,
            "/cats": self._list_user_categories,
            "/boards": self. _list_user_boards,
            "/goal": self._detail_user_goal,
            "/category": self._detail_user_category,
            "/cat": self._detail_user_category,
            "/board": self._detail_user_board,
            "/create": self._create_object
        }

        if command not in user_commands:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text="[unknown command]")
            command = "/help"

        if command == "/help":
            self.tg_client.send_message(chat_id=tg_user.chat_id, text=f"{list(user_commands.keys())}")
        else:
            user_commands[command](tg_user, *params)

    def _list_user_goals(self, tg_user, *args):
        goals = Goal.objects.select_related('user').filter(user=tg_user.user, category__is_deleted=False) \
            .exclude(status=Goal.Status.archived)

        if goals:
            resp_msg = "Ваши цели:\n" + "\n".join([f"#{goal.id} {goal.title}" for goal in goals])
        else:
            resp_msg = "Список ваших целей пуст: []"

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)

    def _list_user_categories(self, tg_user, *args):

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

    def _list_user_boards(self, tg_user: TgUser, *args):
        boards = Board.objects.filter(participants__user_id=tg_user.user_id).exclude(is_deleted=True)

        boards_list = [f'#{board.id}: {board.title}' for board in boards]
        if boards_list:
            resp_msg = 'Доступные доски:\n' + '\n'.join(boards_list)
        else:
            resp_msg = 'У вас нет доступных досок.'

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)

    def _detail_user_goal(self, tg_user, *args):

        resp_msg = "[not correct command]\n" \
                   "use: /goal goal_id\n" \
                   "where goal_id is id number of the goal from /goals"

        if not args:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
            return None

        try:
            goal_id = int(args[0])
        except TypeError:
            if type(goal_id) != int:
                self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
                return None

        goal = Goal.objects.select_related('user').filter(category__is_deleted=False)\
            .exclude(status=Goal.Status.archived).get(id=goal_id)

        resp_msg = f"id: {goal.id}\n" \
                   f"заголовок: {goal.title}\n" \
                   f"статус: {goal.status}\n" \
                   f"категория: {goal.category}\n" \
                   f"приоритет: {goal.priority}\n" \
                   f"создана: {goal.created}\n" \
                   f"дедлайн: {goal.due_date}\n"

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)

    def _detail_user_board(self, tg_user, *args):
        resp_msg = "[not correct command]\n" \
                   "use: /board board_id\n" \
                   "where board_id is id number of the board from /boards"

        if not args:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
            return None

        try:
            board_id = int(args[0])
        except TypeError:
            if type(board_id) != int:
                self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
                return None

        board = Board.objects.filter(participants__user_id=tg_user.user_id).exclude(is_deleted=True).get(id=board_id)

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=board)

    def _detail_user_category(self, tg_user, *args):
        resp_msg = "[not correct command]\n" \
                   "use: /cat cat_id\n" \
                   "where cat_id is id number of the cat from /cats"

        if not args:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
            return None

        try:
            cat_id = int(args[0])
        except TypeError:
            if type(cat_id) != int:
                self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
                return None

        cat = GoalCategory.objects.select_related('user').filter(user=tg_user, is_deleted=False).get(id=cat_id)

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=cat)

    def _create_object(self, tg_user, *args):
        create_obj_dict = {
            "goal": self._create_user_goal
        }

        resp_msg = f"[not correct command]\n" \
                   f"use: /create object\n" \
                   f"where object is in {list(create_obj_dict.keys())}"

        if not args:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
            return None

        obj, *params = args
        if obj not in create_obj_dict.keys():
            self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
            return None

        create_obj_dict[obj](tg_user, *params)

    def _create_user_goal(self, tg_user, *args):
        # /create goal cat_id goal_title with_spaces
        resp_msg = f"[not correct command]\n" \
                   f"use: /create goal cat_id title_with_spaces\n" \
                   f"where cat_id in /cats"
        try:
            cat_id, *title = args
            cat_id = int(cat_id)
            title = " ".join(title)

            category = GoalCategory.objects.filter(
                is_deleted=False,
                board__participants__user=tg_user.user,
                board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
            ).get(id=cat_id)

            Goal.objects.create(title=title, user=tg_user.user, category=category)
            tg_user.save()

        except ValueError:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
            return None
        except Exception as e:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text=e)
            return None

        resp_msg = "Goal created"
        self.tg_client.send_message(chat_id=tg_user.chat_id, text=resp_msg)
