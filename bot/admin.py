from django.contrib import admin
from bot.models import TgUser


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "db_user")
    readonly_fields = ("verification_code",)

    def db_user(self, obj):
        if obj.user:
            return obj.user.username
