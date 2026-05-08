from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..models import PushDeviceToken, User
from ..serializers import PushDeviceTokenSerializer, UserProfileUpdateSerializer, UserReadSerializer


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
def register(request):
    nickname = (request.data.get("nickname") or "").strip()
    password = request.data.get("password") or ""
    first_name = (request.data.get("first_name") or "").strip()
    last_name = (request.data.get("last_name") or "").strip()

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

    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            "token": token.key,
            "user": UserReadSerializer(user, context={"request": request}).data,
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


@api_view(["POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def me_photo(request):
    if request.method == "DELETE":
        if request.user.photo:
            request.user.photo.delete(save=False)
        request.user.photo = None
        request.user.save(update_fields=["photo"])
        return Response(UserReadSerializer(request.user, context={"request": request}).data)

    photo = request.FILES.get("photo")
    if not photo:
        return Response({"photo": "Передайте файл в поле photo."}, status=status.HTTP_400_BAD_REQUEST)
    request.user.photo = photo
    request.user.save(update_fields=["photo"])
    return Response(UserReadSerializer(request.user, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def device_token(request):
    serializer = PushDeviceTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token_value = serializer.validated_data["token"]
    platform = serializer.validated_data.get("platform") or PushDeviceToken.PLATFORM_ANDROID
    token, _ = PushDeviceToken.objects.update_or_create(
        token=token_value,
        defaults={
            "user": request.user,
            "platform": platform,
            "is_active": True,
        },
    )
    return Response(PushDeviceTokenSerializer(token).data, status=status.HTTP_201_CREATED)


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
