from django.urls import path

from user.views.auth import change_password, device_token, login, logout, me, me_photo, register
from user.views.search import UserSearchApi
from user.views.user_api import UserListCreateView

urlpatterns = [
    path("auth/register/", register, name="api-auth-register"),
    path("auth/login/", login, name="api-auth-login"),
    path("auth/logout/", logout, name="api-auth-logout"),
    path("auth/change-password/", change_password, name="api-auth-change-password"),
    path("auth/me/", me, name="api-auth-me"),
    path("auth/me/photo/", me_photo, name="api-auth-me-photo"),
    path("auth/device-token/", device_token, name="api-auth-device-token"),
    path("users/search/", UserSearchApi.as_view(), name="api-users-search"),
    path("users/", UserListCreateView.as_view(), name="api-users"),
]
