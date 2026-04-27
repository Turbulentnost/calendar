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
        extra.setdefault("role", 0.0)
        return self.create_user(nickname, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    """
    0.0 — суперадмин, 1.0 — админ; далее — своя шкала.
    job_title — отображаемое название должности.
    """

    nickname = models.CharField("Никнейм", max_length=150, unique=True, db_index=True)
    first_name = models.CharField("Имя", max_length=150, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, blank=True)
    photo = models.ImageField("Фото профиля", upload_to="users/photos/", blank=True, null=True)
    role = models.FloatField("Роль (0 — суперадмин, 1 — админ)", default=1.0)
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
        return self.role == 0.0 or self.is_superuser

    def is_admin_role(self) -> bool:
        return self.is_staff and self.role in (0.0, 1.0) or self.is_superuser
