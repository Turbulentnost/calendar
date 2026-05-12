from django.contrib import admin

from .models import Project, ProjectActivity, ProjectDailyStatistics, ProjectMembership, ProjectNotification, ProjectTask


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("login", "title", "creator", "name", "room_created_at")
    search_fields = ("login", "title", "name", "description", "creator__nickname")
    autocomplete_fields = ("creator",)


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role", "joined_at")
    list_filter = ("role",)
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


@admin.register(ProjectNotification)
class ProjectNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "recipient", "sender", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "message", "project__title", "recipient__nickname", "sender__nickname")
    autocomplete_fields = ("project", "recipient", "sender")


@admin.register(ProjectDailyStatistics)
class ProjectDailyStatisticsAdmin(admin.ModelAdmin):
    list_display = ("project", "date", "completed_count", "in_progress_count", "overdue_count", "productivity_percent")
    list_filter = ("date",)
    search_fields = ("project__title", "project__login")
    autocomplete_fields = ("project",)


@admin.register(ProjectActivity)
class ProjectActivityAdmin(admin.ModelAdmin):
    list_display = ("project", "actor", "activity_type", "message", "created_at")
    list_filter = ("activity_type", "created_at")
    search_fields = ("project__title", "actor__nickname", "message")
    autocomplete_fields = ("project", "actor", "task")

