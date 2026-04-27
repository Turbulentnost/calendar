from django.apps import AppConfig


class CalendarfuncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "calendarfunc"

    def ready(self):
        import os
        import sys
        import threading
        import time

        skip_commands = {
            "check",
            "collectstatic",
            "createsuperuser",
            "makemigrations",
            "migrate",
            "shell",
            "test",
        }
        if any(command in sys.argv for command in skip_commands):
            return
        if "runserver" in sys.argv and os.environ.get("RUN_MAIN") != "true":
            return

        def run_rollover():
            time.sleep(1)
            try:
                from .services import rollover_overdue_project_tasks_once_per_day

                rollover_overdue_project_tasks_once_per_day()
            except Exception:
                pass

        threading.Thread(target=run_rollover, daemon=True).start()
