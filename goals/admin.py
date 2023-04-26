from django.contrib import admin

from goals.models import GoalCategory, Goal, GoalComment


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title', 'user')


@admin.register(Goal)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'due_date', 'status')
    search_fields = ('title', 'user')


@admin.register(GoalComment)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'goal', 'created', 'updated')
    search_fields = ('text', 'user')
