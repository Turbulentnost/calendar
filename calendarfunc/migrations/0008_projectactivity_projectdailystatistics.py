from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("calendarfunc", "0007_projectnotification_project_login_and_password"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectDailyStatistics",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(verbose_name="Дата")),
                ("completed_count", models.PositiveIntegerField(default=0, verbose_name="Выполнено")),
                ("in_progress_count", models.PositiveIntegerField(default=0, verbose_name="В работе")),
                ("overdue_count", models.PositiveIntegerField(default=0, verbose_name="Просрочено")),
                ("productivity_percent", models.PositiveIntegerField(default=0, verbose_name="Продуктивность")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_statistics",
                        to="calendarfunc.project",
                        verbose_name="Проект",
                    ),
                ),
            ],
            options={
                "verbose_name": "дневная статистика проекта",
                "verbose_name_plural": "дневная статистика проектов",
                "ordering": ["-date"],
                "unique_together": {("project", "date")},
            },
        ),
        migrations.CreateModel(
            name="ProjectActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "activity_type",
                    models.CharField(
                        choices=[
                            ("task_created", "Задача создана"),
                            ("task_updated", "Задача обновлена"),
                            ("task_closed", "Задача закрыта"),
                            ("task_reopened", "Задача открыта"),
                            ("task_carried", "Задача перенесена"),
                            ("member_joined", "Участник вошел"),
                            ("member_left", "Участник вышел"),
                        ],
                        max_length=40,
                        verbose_name="Тип активности",
                    ),
                ),
                ("message", models.CharField(max_length=255, verbose_name="Сообщение")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                (
                    "actor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="project_activities",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Кто сделал",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to="calendarfunc.project",
                        verbose_name="Проект",
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="activities",
                        to="calendarfunc.projecttask",
                        verbose_name="Задача",
                    ),
                ),
            ],
            options={
                "verbose_name": "активность проекта",
                "verbose_name_plural": "активности проектов",
                "ordering": ["-created_at"],
            },
        ),
    ]
