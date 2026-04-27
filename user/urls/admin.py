from django.urls import path

from user.views.admin_users import (
    AdminUserDetailApi,
    AdminUserListCreateApi,
    admin_stats,
    admin_user_reset_password,
)

urlpatterns = [
    path("users/", AdminUserListCreateApi.as_view(), name="admin-users-list-create"),
    path("users/<int:pk>/", AdminUserDetailApi.as_view(), name="admin-users-detail"),
    path(
        "users/<int:pk>/reset-password/",
        admin_user_reset_password,
        name="admin-users-reset-password",
    ),
    path("stats/", admin_stats, name="admin-stats"),
]
