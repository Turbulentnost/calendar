import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("user", "0002_user_department"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название задачи")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "priority",
                    models.CharField(
                        choices=[("low", "Низкий"), ("medium", "Средний"), ("high", "Высокий")],
                        default="medium",
                        max_length=20,
                        verbose_name="Приоритет",
                    ),
                ),
                ("deadline", models.DateField(blank=True, null=True, verbose_name="Дедлайн")),
                ("status", models.CharField(choices=[("new", "Новая")], default="new", max_length=20, verbose_name="Статус")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                (
                    "assignee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assigned_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Исполнитель",
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Постановщик",
                    ),
                ),
            ],
            options={
                "verbose_name": "задача",
                "verbose_name_plural": "задачи",
                "ordering": ["-created_at"],
            },
        ),
    ]
