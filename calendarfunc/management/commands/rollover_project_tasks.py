from django.core.management.base import BaseCommand

from calendarfunc.services import rollover_overdue_project_tasks


class Command(BaseCommand):
    help = "Переносит просроченные невыполненные проектные задачи на сегодня."

    def handle(self, *args, **options):
        updated = rollover_overdue_project_tasks()
        self.stdout.write(self.style.SUCCESS(f"Перенесено задач: {updated}"))
