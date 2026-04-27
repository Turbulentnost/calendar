from django.core.cache import cache
from django.utils import timezone

from .models import ProjectTask


def rollover_overdue_project_tasks(today=None) -> int:
    today = today or timezone.localdate()
    now = timezone.now()
    tasks = ProjectTask.objects.filter(date_to__lt=today, is_closed=False).exclude(status=ProjectTask.STATUS_DONE)
    return tasks.update(
        date_from=today,
        date_to=today,
        importance=ProjectTask.IMPORTANCE_CRITICAL,
        is_carried_over=True,
        carried_over_at=now,
    )


def rollover_overdue_project_tasks_once_per_day() -> int:
    today = timezone.localdate()
    cache_key = f"calendarfunc:project-task-rollover:{today.isoformat()}"
    if cache.get(cache_key):
        return 0
    updated = rollover_overdue_project_tasks(today=today)
    cache.set(cache_key, True, 60 * 60 * 24)
    return updated
