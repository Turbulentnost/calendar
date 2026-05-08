from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project, ProjectMembership, ProjectTask
from .serializers import (
    AdminProjectSerializer,
    ProjectLoginSerializer,
    ProjectMembershipSerializer,
    ProjectNotificationSerializer,
    ProjectSerializer,
    ProjectTaskSerializer,
)
from user.permissions import IsStaffWithAdminRole
from .tokens import create_project_token, decode_project_token
from .services import create_project_invitation_notification, send_project_invitation_push


def _get_project_token(request) -> str:
    return (
        request.headers.get("X-Project-Token")
        or request.data.get("project_token")
        or request.query_params.get("project_token")
        or ""
    ).strip()


def _get_project_from_token(request) -> Project:
    try:
        payload = decode_project_token(_get_project_token(request))
    except ValueError:
        return None
    return Project.objects.filter(pk=payload["project_id"]).first()


def _is_project_member(user, project: Project) -> bool:
    if not user or not user.is_authenticated or not project:
        return False
    return ProjectMembership.objects.filter(project=project, user=user).exists()


def _get_membership(user, project: Project) -> ProjectMembership:
    if not user or not user.is_authenticated or not project:
        return None
    return ProjectMembership.objects.filter(project=project, user=user).first()


def _is_project_admin(user, project: Project) -> bool:
    membership = _get_membership(user, project)
    return bool(user.is_superuser or (membership and membership.is_project_admin()))


def _get_active_project(request) -> Project:
    project = _get_project_from_token(request)
    if not _is_project_member(request.user, project):
        return None
    return project


def _can_manage_project(user, project: Project) -> bool:
    return _is_project_admin(user, project)


class ProjectListCreateApi(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return (
            Project.objects.select_related("creator")
            .filter(memberships__user=self.request.user)
            .distinct()
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        ProjectMembership.objects.get_or_create(
            project=project,
            user=request.user,
            defaults={"role": ProjectMembership.PROJECT_ROLE_ADMIN},
        )
        return Response(
            {
                "project_token": create_project_token(project),
                "project": ProjectSerializer(project, context={"request": request}).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ProjectCatalogListApi(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.select_related("creator").all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class AdminProjectListApi(generics.ListAPIView):
    serializer_class = AdminProjectSerializer
    permission_classes = [IsAuthenticated, IsStaffWithAdminRole]

    def get_queryset(self):
        return (
            Project.objects.select_related("creator")
            .annotate(
                members_count=Count("memberships", distinct=True),
                tasks_count=Count("tasks", distinct=True),
            )
            .order_by("-room_created_at")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ProjectDetailApi(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return (
            Project.objects.select_related("creator")
            .filter(memberships__user=self.request.user)
            .distinct()
        )

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        if not _can_manage_project(request.user, project):
            return Response(
                {"detail": "Недостаточно прав для изменения проекта."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if not _can_manage_project(request.user, project):
            return Response(
                {"detail": "Недостаточно прав для удаления проекта."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ProjectLoginApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProjectLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = Project.objects.filter(login=serializer.validated_data["login"]).first()
        if not project or not project.check_password(serializer.validated_data["password"]):
            return Response(
                {"detail": "Неверный логин или пароль проекта."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ProjectMembership.objects.get_or_create(
            project=project,
            user=request.user,
            defaults={"role": ProjectMembership.PROJECT_ROLE_MEMBER},
        )
        return Response(
            {
                "project_token": create_project_token(project),
                "project": ProjectSerializer(project, context={"request": request}).data,
            }
        )


class ProjectCurrentApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project = _get_active_project(request)
        if not project:
            return Response(
                {"detail": "Укажите корректный токен проекта."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(ProjectSerializer(project, context={"request": request}).data)


class ProjectInviteApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project = _get_active_project(request)
        if not project or not _is_project_admin(request.user, project):
            return Response(
                {"detail": "Недостаточно прав для приглашения пользователей."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"user_id": "Укажите пользователя."}, status=status.HTTP_400_BAD_REQUEST)
        project_login = (request.data.get("project_login") or "").strip()
        project_password = request.data.get("project_password") or ""
        if not project_login:
            return Response({"project_login": "Укажите логин проекта."}, status=status.HTTP_400_BAD_REQUEST)
        if not project_password:
            return Response({"project_password": "Укажите пароль проекта."}, status=status.HTTP_400_BAD_REQUEST)
        user_model = ProjectMembership._meta.get_field("user").remote_field.model
        recipient = get_object_or_404(user_model, pk=user_id)
        if ProjectMembership.objects.filter(project=project, user=recipient).exists():
            return Response(
                {"detail": "Пользователь уже состоит в проекте."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        notification = create_project_invitation_notification(
            project=project,
            sender=request.user,
            recipient=recipient,
            project_login=project_login,
            project_password=project_password,
        )
        push_sent = send_project_invitation_push(notification)
        data = ProjectNotificationSerializer(notification, context={"request": request}).data
        data["push_sent"] = push_sent
        return Response(
            data,
            status=status.HTTP_201_CREATED,
        )


class ProjectNotificationListApi(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        return (
            request.user.project_notifications
            .select_related("project", "sender")
            .all()
        )

    def get(self, request):
        try:
            serializer = ProjectNotificationSerializer(
                self.get_queryset(request),
                many=True,
                context={"request": request},
            )
            return Response(serializer.data)
        except (OperationalError, ProgrammingError):
            return Response(
                {"detail": "Таблица уведомлений ещё не создана. Примените миграции backend."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def delete(self, request):
        try:
            deleted_count, _ = self.get_queryset(request).delete()
            return Response({"deleted": deleted_count})
        except (OperationalError, ProgrammingError):
            return Response(
                {"detail": "Таблица уведомлений ещё не создана. Примените миграции backend."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class ProjectMemberListApi(generics.ListAPIView):
    serializer_class = ProjectMembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project = _get_active_project(self.request)
        if not project:
            return ProjectMembership.objects.none()
        return ProjectMembership.objects.select_related("project", "user").filter(project=project)


class ProjectMemberDetailApi(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectMembershipSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "user_id"
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        project = _get_active_project(self.request)
        if not project:
            return ProjectMembership.objects.none()
        return ProjectMembership.objects.select_related("project", "user").filter(project=project)

    def update(self, request, *args, **kwargs):
        project = _get_active_project(request)
        if not project or not _is_project_admin(request.user, project):
            return Response(
                {"detail": "Недостаточно прав для изменения ролей проекта."},
                status=status.HTTP_403_FORBIDDEN,
            )
        membership = self.get_object()
        new_role = request.data.get("role")
        if new_role is None:
            return Response({"role": "Укажите роль в проекте."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_role = float(new_role)
        except (TypeError, ValueError):
            return Response({"role": "Роль должна быть числом."}, status=status.HTTP_400_BAD_REQUEST)
        if membership.is_project_admin() and new_role > ProjectMembership.PROJECT_ROLE_ADMIN:
            admin_count = ProjectMembership.objects.filter(
                project=project,
                role__lte=ProjectMembership.PROJECT_ROLE_ADMIN,
            ).count()
            if admin_count <= 1:
                return Response(
                    {"detail": "В проекте должен остаться хотя бы один админ."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        membership.role = new_role
        membership.save(update_fields=["role"])
        return Response(ProjectMembershipSerializer(membership, context={"request": request}).data)

    def destroy(self, request, *args, **kwargs):
        project = _get_active_project(request)
        if not project or not _is_project_admin(request.user, project):
            return Response(
                {"detail": "Недостаточно прав для удаления участников проекта."},
                status=status.HTTP_403_FORBIDDEN,
            )
        membership = self.get_object()
        if membership.is_project_admin():
            admin_count = ProjectMembership.objects.filter(
                project=project,
                role__lte=ProjectMembership.PROJECT_ROLE_ADMIN,
            ).count()
            if admin_count <= 1:
                return Response(
                    {"detail": "В проекте должен остаться хотя бы один админ."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectTaskListCreateApi(generics.ListCreateAPIView):
    serializer_class = ProjectTaskSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_project(self):
        project = _get_active_project(self.request)
        if not project:
            raise PermissionDenied("Укажите корректный токен проекта.")
        return project

    def get_queryset(self):
        try:
            project = self.get_project()
        except PermissionDenied:
            return ProjectTask.objects.none()
        return (
            ProjectTask.objects.select_related("project", "author", "assignee")
            .filter(project=project)
            .filter(
                Q(author=self.request.user)
                | Q(assignee=self.request.user)
                | Q(project__memberships__user=self.request.user, project__memberships__role__lte=ProjectMembership.PROJECT_ROLE_ADMIN)
            )
            .distinct()
        )

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        is_closed = self.request.query_params.get("is_closed")
        importance = self.request.query_params.get("importance")
        status_value = self.request.query_params.get("status")
        assigned_to_me = self.request.query_params.get("assigned_to_me")
        authored_by_me = self.request.query_params.get("authored_by_me")

        if is_closed in ("true", "false", "1", "0"):
            queryset = queryset.filter(is_closed=is_closed in ("true", "1"))
        if importance:
            queryset = queryset.filter(importance=importance)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if assigned_to_me in ("true", "1"):
            queryset = queryset.filter(assignee=self.request.user)
        if authored_by_me in ("true", "1"):
            queryset = queryset.filter(author=self.request.user)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        context["project"] = self.get_project()
        return context


class ProjectTaskDetailApi(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectTaskSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        project = _get_active_project(self.request)
        if not project:
            return ProjectTask.objects.none()
        return (
            ProjectTask.objects.select_related("project", "author", "assignee")
            .filter(project=project)
            .filter(
                Q(author=self.request.user)
                | Q(assignee=self.request.user)
                | Q(project__memberships__user=self.request.user, project__memberships__role__lte=ProjectMembership.PROJECT_ROLE_ADMIN)
            )
            .distinct()
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        context["project"] = self.get_object().project
        return context


class ProjectTaskCloseApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        project = _get_active_project(request)
        if not project:
            return Response(
                {"detail": "Укажите корректный токен проекта."},
                status=status.HTTP_403_FORBIDDEN,
            )
        task = get_object_or_404(
            ProjectTask.objects.select_related("project", "author", "assignee"),
            pk=pk,
            project=project,
        )
        if (
            task.author_id != request.user.id
            and task.assignee_id != request.user.id
            and not _is_project_admin(request.user, project)
        ):
            return Response(
                {"detail": "Недостаточно прав для закрытия задачи."},
                status=status.HTTP_403_FORBIDDEN,
            )
        task.is_closed = True
        task.status = ProjectTask.STATUS_DONE
        task.save(update_fields=["is_closed", "status", "updated_at"])
        return Response(ProjectTaskSerializer(task, context={"request": request, "project": project}).data)


class ProjectTaskReopenApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        project = _get_active_project(request)
        if not project:
            return Response(
                {"detail": "Укажите корректный токен проекта."},
                status=status.HTTP_403_FORBIDDEN,
            )
        task = get_object_or_404(
            ProjectTask.objects.select_related("project", "author", "assignee"),
            pk=pk,
            project=project,
        )
        if task.author_id != request.user.id and not _is_project_admin(request.user, project):
            return Response(
                {"detail": "Только автор задачи может открыть её заново."},
                status=status.HTTP_403_FORBIDDEN,
            )
        task.is_closed = False
        task.status = ProjectTask.STATUS_IN_PROGRESS
        task.save(update_fields=["is_closed", "status", "updated_at"])
        return Response(ProjectTaskSerializer(task, context={"request": request, "project": project}).data)


class ProjectTaskCarryOverApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        project = _get_active_project(request)
        if not project:
            return Response(
                {"detail": "Укажите корректный токен проекта."},
                status=status.HTTP_403_FORBIDDEN,
            )
        task = get_object_or_404(
            ProjectTask.objects.select_related("project", "author", "assignee"),
            pk=pk,
            project=project,
        )
        if (
            task.author_id != request.user.id
            and task.assignee_id != request.user.id
            and not _is_project_admin(request.user, project)
        ):
            return Response(
                {"detail": "Недостаточно прав для переноса задачи."},
                status=status.HTTP_403_FORBIDDEN,
            )
        today = timezone.localdate()
        task.date_from = today
        task.date_to = today
        task.importance = ProjectTask.IMPORTANCE_CRITICAL
        task.is_carried_over = True
        task.carried_over_at = timezone.now()
        task.save(
            update_fields=[
                "date_from",
                "date_to",
                "importance",
                "is_carried_over",
                "carried_over_at",
                "updated_at",
            ]
        )
        return Response(ProjectTaskSerializer(task, context={"request": request, "project": project}).data)
