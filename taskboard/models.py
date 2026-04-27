from django.conf import settings
from django.db import models


class Task(models.Model):
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, "Низкий"),
        (PRIORITY_MEDIUM, "Средний"),
        (PRIORITY_HIGH, "Высокий"),
    )

    STATUS_NEW = "new"
    STATUS_CHOICES = (
        (STATUS_NEW, "Новая"),
    )

    title = models.CharField("Название задачи", max_length=255)
    description = models.TextField("Описание", blank=True)
    priority = models.CharField("Приоритет", max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    deadline = models.DateField("Дедлайн", blank=True, null=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_tasks",
        on_delete=models.CASCADE,
        verbose_name="Постановщик",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_tasks",
        on_delete=models.CASCADE,
        verbose_name="Исполнитель",
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "задача"
        verbose_name_plural = "задачи"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
