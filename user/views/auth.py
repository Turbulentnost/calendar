from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from calendarfunc.models import Project
from calendarfunc.serializers import ProjectSerializer
from calendarfunc.tokens import create_project_token
from ..models import User
from ..serializers import UserProfileUpdateSerializer, UserReadSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    nickname = (request.data.get("nickname") or "").strip()
    password = request.data.get("password") or ""
    if not nickname:
        return Response({"detail": "Укажите никнейм."}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(request, username=nickname, password=password)
    if not user or not user.is_active:
        return Response({"detail": "Неверные данные."}, status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            "token": token.key,
            "user": UserReadSerializer(user, context={"request": request}).data,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def register(request):
    nickname = (request.data.get("nickname") or "").strip()
    password = request.data.get("password") or ""
    first_name = (request.data.get("first_name") or "").strip()
    last_name = (request.data.get("last_name") or "").strip()
    project_action = (request.data.get("project_action") or "").strip()

    if not nickname:
        return Response({"detail": "Укажите никнейм."}, status=status.HTTP_400_BAD_REQUEST)
    if not password:
        return Response({"detail": "Укажите пароль пользователя."}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(nickname=nickname).exists():
        return Response({"detail": "Никнейм уже занят."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        nickname=nickname,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )

    project = None
    if project_action == "create_project":
        project_data = request.data.get("project") or {}
        serializer = ProjectSerializer(
            data=project_data,
            context={"request": type("RequestContext", (), {"user": user})()},
        )
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
    elif project_action == "join_project":
        project_login = (request.data.get("project_login") or "").strip()
        project_password = request.data.get("project_password") or ""
        project = Project.objects.filter(login=project_login).first()
        if not project or not project.check_password(project_password):
            return Response(
                {"detail": "Неверный логин или пароль проекта."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        return Response(
            {"detail": "Укажите project_action: create_project или join_project."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            "token": token.key,
            "project_token": create_project_token(project),
            "user": UserReadSerializer(user, context={"request": request}).data,
            "project": ProjectSerializer(project, context={"request": request}).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PATCH", "PUT"])
@permission_classes([IsAuthenticated])
def me(request):
    if request.method == "GET":
        return Response(UserReadSerializer(request.user, context={"request": request}).data)

    serializer = UserProfileUpdateSerializer(
        request.user,
        data=request.data,
        partial=request.method == "PATCH",
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(UserReadSerializer(request.user, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    old_password = request.data.get("old_password") or ""
    new_password = request.data.get("new_password") or ""
    if not request.user.check_password(old_password):
        return Response({"detail": "Неверный текущий пароль."}, status=status.HTTP_400_BAD_REQUEST)
    if not new_password:
        return Response({"detail": "Укажите новый пароль."}, status=status.HTTP_400_BAD_REQUEST)
    request.user.set_password(new_password)
    request.user.save(update_fields=["password"])
    Token.objects.filter(user=request.user).delete()
    token, _ = Token.objects.get_or_create(user=request.user)
    return Response({"token": token.key})
