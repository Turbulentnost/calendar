from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import User
from ..permissions import IsStaffWithAdminRole
from ..serializers import AdminUserSerializer


def _is_superadmin(user: User) -> bool:
    return bool(user.is_superadmin())


def _can_manage_target(actor: User, target: User) -> bool:
    if _is_superadmin(actor):
        return True
    if target.pk == actor.pk:
        return True
    if actor.app_role == User.APP_ROLE_ADMIN and target.app_role in (
        User.APP_ROLE_SUPERADMIN,
        User.APP_ROLE_ADMIN,
    ):
        return False
    return True


def _to_bool(val):
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("1", "true", "yes", "on")


class AdminUserListCreateApi(APIView):
    permission_classes = [IsAuthenticated, IsStaffWithAdminRole]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        qs = User.objects.all().order_by("nickname")
        q = (request.query_params.get("q") or "").strip()
        role = (request.query_params.get("role") or request.query_params.get("app_role") or "").strip()
        job_title = (request.query_params.get("job_title") or "").strip()
        department = (request.query_params.get("department") or "").strip()

        if q:
            qs = qs.filter(
                Q(nickname__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(department__icontains=q)
            )
        if role in dict(User.APP_ROLE_CHOICES):
            qs = qs.filter(app_role=role)
        if job_title:
            qs = qs.filter(job_title__icontains=job_title)
        if department:
            qs = qs.filter(department__icontains=department)

        total = qs.count()
        page = max(int(request.query_params.get("page", 1) or 1), 1)
        page_size = int(request.query_params.get("page_size", 10) or 10)
        page_size = min(max(page_size, 1), 100)
        start = (page - 1) * page_size
        items = qs[start : start + page_size]

        serializer = AdminUserSerializer(
            items,
            many=True,
            context={"request": request},
        )
        return Response(
            {
                "results": serializer.data,
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size if total else 1,
            }
        )

    def post(self, request):
        data = request.data.copy()
        if "is_staff" not in data:
            data["is_staff"] = True
        data["is_staff"] = _to_bool(data["is_staff"])
        if "is_active" in data:
            data["is_active"] = _to_bool(data["is_active"])
        serializer = AdminUserSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()
        return Response(
            AdminUserSerializer(new_user, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AdminUserDetailApi(APIView):
    permission_classes = [IsAuthenticated, IsStaffWithAdminRole]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk: int):
        user = self.get_object(pk)
        return Response(AdminUserSerializer(user, context={"request": request}).data)

    def put(self, request, pk: int):
        user = self.get_object(pk)
        if not _can_manage_target(request.user, user):
            return Response(
                {"detail": "Недостаточно прав для редактирования этого пользователя."},
                status=status.HTTP_403_FORBIDDEN,
            )
        data = request.data.copy()
        if "is_staff" in data:
            data["is_staff"] = _to_bool(data["is_staff"])
        if "is_active" in data:
            data["is_active"] = _to_bool(data["is_active"])
        serializer = AdminUserSerializer(
            user,
            data=data,
            partial=False,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk: int):
        user = self.get_object(pk)
        if not _can_manage_target(request.user, user):
            return Response(
                {"detail": "Недостаточно прав для удаления этого пользователя."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if user.pk == request.user.pk:
            return Response(
                {"detail": "Нельзя удалить собственный аккаунт."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStaffWithAdminRole])
def admin_user_reset_password(request, pk: int):
    user = get_object_or_404(User, pk=pk)
    if not _can_manage_target(request.user, user):
        return Response(
            {"detail": "Недостаточно прав для сброса пароля этого пользователя."},
            status=status.HTTP_403_FORBIDDEN,
        )

    temp_password = get_random_string(10)
    user.set_password(temp_password)
    user.save(update_fields=["password"])
    return Response(
        {"detail": "Временный пароль сгенерирован.", "temp_password": temp_password}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStaffWithAdminRole])
def admin_stats(request):
    total = User.objects.count()
    superadmins = User.objects.filter(app_role=User.APP_ROLE_SUPERADMIN).count()
    admins = User.objects.filter(app_role=User.APP_ROLE_ADMIN).count()
    return Response(
        {
            "total_users": total,
            "superadmins": superadmins,
            "admins": admins,
        }
    )
