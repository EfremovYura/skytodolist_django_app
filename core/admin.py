from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "email")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("username", "first_name", "last_name", "email")
    readonly_fields = ("last_login", "date_joined")
    exclude = ("password",)
    ordering = ('email',)

