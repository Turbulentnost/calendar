from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, nickname, password=None, **extra):
        if not nickname:
            raise ValueError("Нужен nickname")
        user = self.model(nickname=nickname, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nickname, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)
        extra.setdefault("app_role", User.APP_ROLE_SUPERADMIN)
        extra.setdefault("role", 0.0)
        return self.create_user(nickname, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    """
    app_role — глобальная роль приложения.
    role — устаревшее числовое поле, проектные роли хранятся в ProjectMembership.
    job_title — отображаемое название должности.
    """

    APP_ROLE_SUPERADMIN = "superadmin"
    APP_ROLE_ADMIN = "admin"
    APP_ROLE_USER = "user"
    APP_ROLE_GUEST = "guest"
    APP_ROLE_CHOICES = (
        (APP_ROLE_SUPERADMIN, "Суперадмин"),
        (APP_ROLE_ADMIN, "Админ"),
        (APP_ROLE_USER, "Пользователь"),
        (APP_ROLE_GUEST, "Гость"),
    )

    nickname = models.CharField("Никнейм", max_length=150, unique=True, db_index=True)
    first_name = models.CharField("Имя", max_length=150, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, blank=True)
    photo = models.ImageField("Фото профиля", upload_to="users/photos/", blank=True, null=True)
    app_role = models.CharField(
        "Роль в приложении",
        max_length=20,
        choices=APP_ROLE_CHOICES,
        default=APP_ROLE_USER,
    )
    role = models.FloatField("Устаревшая числовая роль", default=10.0)
    department = models.CharField("Отдел", max_length=255, blank=True)
    job_title = models.CharField("Название должности", max_length=255, blank=True)

    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Доступ в админку", default=False)
    is_superuser = models.BooleanField("Суперпользователь", default=False)
    date_joined = models.DateTimeField("Дата регистрации", default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "nickname"
    REQUIRED_FIELDS: list = []

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ["nickname"]

    def __str__(self) -> str:
        return self.nickname

    def get_full_name(self) -> str:
        parts = (self.first_name, self.last_name)
        s = " ".join(p for p in parts if p)
        return s or self.nickname

    def is_superadmin(self) -> bool:
        return self.app_role == self.APP_ROLE_SUPERADMIN or self.is_superuser

    def is_admin_role(self) -> bool:
        return self.app_role in (self.APP_ROLE_SUPERADMIN, self.APP_ROLE_ADMIN) or self.is_superuser


class PushDeviceToken(models.Model):
    PLATFORM_ANDROID = "android"
    PLATFORM_IOS = "ios"
    PLATFORM_WEB = "web"
    PLATFORM_CHOICES = (
        (PLATFORM_ANDROID, "Android"),
        (PLATFORM_IOS, "iOS"),
        (PLATFORM_WEB, "Web"),
    )

    user = models.ForeignKey(
        User,
        related_name="push_device_tokens",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    token = models.CharField("Device token", max_length=512, unique=True)
    platform = models.CharField(
        "Платформа",
        max_length=20,
        choices=PLATFORM_CHOICES,
        default=PLATFORM_ANDROID,
    )
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    class Meta:
        verbose_name = "push token устройства"
        verbose_name_plural = "push tokens устройств"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.user} {self.platform}"
