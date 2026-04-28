from django.contrib import admin

from .models import Project, ProjectMembership, ProjectTask


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("login", "title", "creator", "name", "room_created_at")
    search_fields = ("login", "title", "name", "description", "creator__nickname")
    autocomplete_fields = ("creator",)


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "joined_at")
    search_fields = ("project__login", "project__title", "user__nickname")
    autocomplete_fields = ("project", "user")


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = (
        "short_description",
        "project",
        "author",
        "assignee",
        "date_from",
        "date_to",
        "importance",
        "status",
        "is_closed",
        "is_carried_over",
    )
    list_filter = ("importance", "status", "is_closed", "is_carried_over", "date_from", "date_to")
    search_fields = (
        "short_description",
        "description",
        "project__title",
        "author__nickname",
        "assignee__nickname",
    )
    autocomplete_fields = ("project", "author", "assignee")

