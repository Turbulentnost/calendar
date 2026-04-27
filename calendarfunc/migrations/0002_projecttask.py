import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("calendarfunc", "0001_initial"),
        ("user", "0003_user_projects"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_from", models.DateField(verbose_name="От какого числа")),
                ("date_to", models.DateField(verbose_name="До какого числа")),
                ("short_description", models.CharField(max_length=255, verbose_name="Основное описание")),
                ("description", models.TextField(blank=True, verbose_name="Развернутое описание")),
                ("deadline", models.DateTimeField(blank=True, null=True, verbose_name="Срок")),
                (
                    "importance",
                    models.CharField(
                        choices=[("normal", "Обычная"), ("high", "Высокая"), ("critical", "Критическая")],
                        default="normal",
                        max_length=20,
                        verbose_name="Важность",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("new", "Новая"), ("in_progress", "В работе"), ("done", "Выполнена")],
                        default="new",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                ("carried_over_at", models.DateTimeField(blank=True, null=True, verbose_name="Перенесено")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                (
                    "assignee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assigned_project_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Кому предназначена",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="authored_project_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="calendarfunc.project",
                        verbose_name="Проект",
                    ),
                ),
            ],
            options={
                "verbose_name": "задача проекта",
                "verbose_name_plural": "задачи проектов",
                "ordering": ["date_from", "created_at"],
            },
        ),
    ]
