from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "assignee", "priority", "status", "deadline", "created_at")
    list_filter = ("priority", "status", "deadline")
    search_fields = ("title", "description", "creator__nickname", "assignee__nickname")
    autocomplete_fields = ("creator", "assignee")
