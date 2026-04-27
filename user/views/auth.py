from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..serializers import UserReadSerializer


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserReadSerializer(request.user, context={"request": request}).data)
