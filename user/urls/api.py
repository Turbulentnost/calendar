from django.urls import path

from user.views.auth import login, me
from user.views.user_api import UserListCreateView

urlpatterns = [
    path("auth/login/", login, name="api-auth-login"),
    path("auth/me/", me, name="api-auth-me"),
    path("users/", UserListCreateView.as_view(), name="api-users"),
]
