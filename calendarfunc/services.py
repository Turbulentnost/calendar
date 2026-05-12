from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import json
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError

from .models import Project, ProjectActivity, ProjectDailyStatistics, ProjectNotification, ProjectTask


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


def create_project_invitation_notification(
    *,
    project: Project,
    sender,
    recipient,
    project_login: str,
    project_password: str,
) -> ProjectNotification:
    return ProjectNotification.objects.create(
        project=project,
        sender=sender,
        recipient=recipient,
        notification_type=ProjectNotification.TYPE_INVITATION,
        title=f"Приглашение в проект {project.title}",
        message=(
            f"{sender.nickname} приглашает вас в проект {project.title}. "
            f"Логин: {project_login}. Пароль: {project_password}."
        ),
        project_login=project_login,
        project_password=project_password,
    )


def send_project_invitation_push(notification: ProjectNotification) -> int:
    server_key = getattr(settings, "FCM_SERVER_KEY", "")
    if not server_key:
        return 0

    tokens = list(
        notification.recipient.push_device_tokens
        .filter(is_active=True)
        .values_list("token", flat=True)
    )
    sent = 0
    for token in tokens:
        payload = {
            "to": token,
            "notification": {
                "title": notification.title,
                "body": notification.message,
            },
            "data": {
                "type": notification.notification_type,
                "project_id": str(notification.project_id),
                "project_login": notification.project_login,
                "project_password": notification.project_password,
                "notification_id": str(notification.id),
            },
        }
        req = urlrequest.Request(
            getattr(settings, "FCM_LEGACY_URL", "https://fcm.googleapis.com/fcm/send"),
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"key={server_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=5) as response:
                if 200 <= response.status < 300:
                    sent += 1
        except (HTTPError, URLError, TimeoutError):
            continue
    return sent


def log_project_activity(*, project: Project, actor, activity_type: str, message: str, task=None) -> ProjectActivity:
    return ProjectActivity.objects.create(
        project=project,
        actor=actor,
        task=task,
        activity_type=activity_type,
        message=message,
    )


def sync_project_daily_statistics(project: Project, date=None) -> ProjectDailyStatistics:
    date = date or timezone.localdate()
    tasks = ProjectTask.objects.filter(project=project, date_from__lte=date, date_to__gte=date)
    completed_count = tasks.filter(status=ProjectTask.STATUS_DONE).count()
    in_progress_count = tasks.filter(status=ProjectTask.STATUS_IN_PROGRESS).count()
    overdue_count = ProjectTask.objects.filter(
        project=project,
        date_to__lt=date,
        is_closed=False,
    ).exclude(status=ProjectTask.STATUS_DONE).count()
    total = tasks.count()
    productivity_percent = round((completed_count / total) * 100) if total else 0
    statistics, _ = ProjectDailyStatistics.objects.update_or_create(
        project=project,
        date=date,
        defaults={
            "completed_count": completed_count,
            "in_progress_count": in_progress_count,
            "overdue_count": overdue_count,
            "productivity_percent": productivity_percent,
        },
    )
    return statistics
