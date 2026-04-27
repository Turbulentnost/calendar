"""Создаёт базу PostgreSQL из DATABASES['default'], если её ещё нет."""

from django.core.management.base import BaseCommand

from core.services.database import ensure_default_database_exists


class Command(BaseCommand):
    help = "Подключиться к серверу PG и CREATE DATABASE для имени из настроек, если базы нет."

    def add_arguments(self, parser):
        parser.add_argument(
            "--maintenance-db",
            default="postgres",
            help="Служебная база для подключения (по умолчанию postgres).",
        )

    def handle(self, *args, **options):
        maintenance = options["maintenance_db"]
        outcome = ensure_default_database_exists(maintenance_dbname=maintenance)
        db_name = self._default_db_name()

        if outcome == "exists":
            self.stdout.write(
                self.style.SUCCESS(f'База "{db_name}" уже существует.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Создана база "{db_name}".')
            )

    def _default_db_name(self):
        from django.conf import settings

        return settings.DATABASES["default"]["NAME"]
