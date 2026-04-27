import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название проекта")),
                ("room_created_at", models.DateTimeField(auto_now_add=True, verbose_name="Когда создана комната")),
                ("name", models.CharField(blank=True, max_length=255, verbose_name="Название комнаты")),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="projects/images/",
                        verbose_name="Изображение",
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_projects",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Создатель проекта",
                    ),
                ),
            ],
            options={
                "verbose_name": "проект",
                "verbose_name_plural": "проекты",
                "ordering": ["-room_created_at"],
            },
        ),
        migrations.CreateModel(
            name="ProjectInvitation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.CharField(db_index=True, max_length=64, unique=True, verbose_name="Токен приглашения")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("used_at", models.DateTimeField(blank=True, null=True, verbose_name="Использовано")),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_project_invitations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Кто создал приглашение",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invitations",
                        to="calendarfunc.project",
                        verbose_name="Проект",
                    ),
                ),
            ],
            options={
                "verbose_name": "приглашение в проект",
                "verbose_name_plural": "приглашения в проекты",
                "ordering": ["-created_at"],
            },
        ),
    ]
