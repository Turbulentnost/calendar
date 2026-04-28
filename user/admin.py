from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("nickname", "first_name", "last_name", "app_role", "department", "job_title", "is_staff", "is_active")
    list_filter = ("app_role", "is_staff", "is_active", "is_superuser")
    search_fields = ("nickname", "first_name", "last_name", "department", "job_title")
    ordering = ("nickname",)
    fieldsets = (
        (None, {"fields": ("nickname", "password")}),
        (_("Персональные данные"), {"fields": ("first_name", "last_name", "photo", "department", "job_title")}),
        (
            _("Права"),
            {
                "fields": (
                    "app_role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Даты"), {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "nickname",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "department",
                    "job_title",
                    "app_role",
                    "photo",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    readonly_fields = ("date_joined", "last_login")
    filter_horizontal = ("groups", "user_permissions")
