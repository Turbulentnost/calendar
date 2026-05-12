from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password


class Project(models.Model):
    login = models.CharField("Логин проекта", max_length=150, unique=True, blank=True, null=True)
    title = models.CharField("Название проекта", max_length=255)
    password_hash = models.CharField("Пароль проекта", max_length=128, blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_projects",
        on_delete=models.CASCADE,
        verbose_name="Создатель проекта",
    )
    room_created_at = models.DateTimeField("Когда создана комната", auto_now_add=True)
    name = models.CharField("Название комнаты", max_length=255, blank=True)
    image = models.ImageField(
        "Изображение",
        upload_to="projects/images/",
        blank=True,
        null=True,
    )
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "проект"
        verbose_name_plural = "проекты"
        ordering = ["-room_created_at"]

    def __str__(self) -> str:
        return self.title

    def set_password(self, raw_password: str):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password_hash)


class ProjectMembership(models.Model):
    PROJECT_ROLE_ADMIN = 1.0
    PROJECT_ROLE_MEMBER = 10.0

    project = models.ForeignKey(
        Project,
        related_name="memberships",
        on_delete=models.CASCADE,
        verbose_name="Проект",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="project_memberships",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    role = models.FloatField("Роль в проекте", default=PROJECT_ROLE_MEMBER)
    joined_at = models.DateTimeField("Дата входа в проект", auto_now_add=True)

    class Meta:
        verbose_name = "участник проекта"
        verbose_name_plural = "участники проектов"
        unique_together = ("project", "user")
        ordering = ["-joined_at"]

    def __str__(self) -> str:
        return f"{self.user} -> {self.project}"

    def is_project_admin(self) -> bool:
        return self.role <= self.PROJECT_ROLE_ADMIN


class ProjectNotification(models.Model):
    TYPE_INVITATION = "project_invitation"
    TYPE_CHOICES = (
        (TYPE_INVITATION, "Приглашение в проект"),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="project_notifications",
        on_delete=models.CASCADE,
        verbose_name="Получатель",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sent_project_notifications",
        on_delete=models.CASCADE,
        verbose_name="Отправитель",
    )
    project = models.ForeignKey(
        Project,
        related_name="notifications",
        on_delete=models.CASCADE,
        verbose_name="Проект",
    )
    notification_type = models.CharField(
        "Тип уведомления",
        max_length=40,
        choices=TYPE_CHOICES,
        default=TYPE_INVITATION,
    )
    title = models.CharField("Заголовок", max_length=255)
    message = models.TextField("Сообщение", blank=True)
    project_login = models.CharField("Логин проекта в приглашении", max_length=150, blank=True)
    project_password = models.CharField("Пароль проекта в приглашении", max_length=255, blank=True)
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "уведомление проекта"
        verbose_name_plural = "уведомления проектов"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class ProjectDailyStatistics(models.Model):
    project = models.ForeignKey(
        Project,
        related_name="daily_statistics",
        on_delete=models.CASCADE,
        verbose_name="Проект",
    )
    date = models.DateField("Дата")
    completed_count = models.PositiveIntegerField("Выполнено", default=0)
    in_progress_count = models.PositiveIntegerField("В работе", default=0)
    overdue_count = models.PositiveIntegerField("Просрочено", default=0)
    productivity_percent = models.PositiveIntegerField("Продуктивность", default=0)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "дневная статистика проекта"
        verbose_name_plural = "дневная статистика проектов"
        unique_together = ("project", "date")
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.project} {self.date}"


class ProjectActivity(models.Model):
    TYPE_TASK_CREATED = "task_created"
    TYPE_TASK_UPDATED = "task_updated"
    TYPE_TASK_CLOSED = "task_closed"
    TYPE_TASK_REOPENED = "task_reopened"
    TYPE_TASK_CARRIED = "task_carried"
    TYPE_MEMBER_JOINED = "member_joined"
    TYPE_MEMBER_LEFT = "member_left"
    TYPE_CHOICES = (
        (TYPE_TASK_CREATED, "Задача создана"),
        (TYPE_TASK_UPDATED, "Задача обновлена"),
        (TYPE_TASK_CLOSED, "Задача закрыта"),
        (TYPE_TASK_REOPENED, "Задача открыта"),
        (TYPE_TASK_CARRIED, "Задача перенесена"),
        (TYPE_MEMBER_JOINED, "Участник вошел"),
        (TYPE_MEMBER_LEFT, "Участник вышел"),
    )

    project = models.ForeignKey(
        Project,
        related_name="activities",
        on_delete=models.CASCADE,
        verbose_name="Проект",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="project_activities",
        on_delete=models.CASCADE,
        verbose_name="Кто сделал",
    )
    task = models.ForeignKey(
        "ProjectTask",
        related_name="activities",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Задача",
    )
    activity_type = models.CharField("Тип активности", max_length=40, choices=TYPE_CHOICES)
    message = models.CharField("Сообщение", max_length=255)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "активность проекта"
        verbose_name_plural = "активности проектов"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.message


class ProjectTask(models.Model):
    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    STATUS_CHOICES = (
        (STATUS_NEW, "Новая"),
        (STATUS_IN_PROGRESS, "В работе"),
        (STATUS_DONE, "Выполнена"),
    )

    IMPORTANCE_NORMAL = "normal"
    IMPORTANCE_HIGH = "high"
    IMPORTANCE_CRITICAL = "critical"
    IMPORTANCE_CHOICES = (
        (IMPORTANCE_NORMAL, "Обычная"),
        (IMPORTANCE_HIGH, "Высокая"),
        (IMPORTANCE_CRITICAL, "Критическая"),
    )

    project = models.ForeignKey(
        Project,
        related_name="tasks",
        on_delete=models.CASCADE,
        verbose_name="Проект",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="authored_project_tasks",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_project_tasks",
        on_delete=models.CASCADE,
        verbose_name="Кому предназначена",
    )
    date_from = models.DateField("От какого числа")
    date_to = models.DateField("До какого числа")
    short_description = models.CharField("Основное описание", max_length=255)
    description = models.TextField("Развернутое описание", blank=True)
    deadline = models.DateTimeField("Срок", blank=True, null=True)
    importance = models.CharField(
        "Важность",
        max_length=20,
        choices=IMPORTANCE_CHOICES,
        default=IMPORTANCE_NORMAL,
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )
    is_closed = models.BooleanField("Закрыта", default=False)
    is_carried_over = models.BooleanField("Перенесена", default=False)
    carried_over_at = models.DateTimeField("Перенесено", blank=True, null=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "задача проекта"
        verbose_name_plural = "задачи проектов"
        ordering = ["date_from", "created_at"]

    def __str__(self) -> str:
        return self.short_description
