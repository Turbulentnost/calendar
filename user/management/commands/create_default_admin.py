from django.core.management.base import BaseCommand

from user.models import User


class Command(BaseCommand):
    help = "Создать (или сбросить пароль) пользователя admin / admin (суперадмин, роль 0.0)."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            nickname="admin",
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "job_title": "Суперадминистратор",
                "role": 0.0,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        user.set_password("admin")
        user.first_name = "Admin"
        user.last_name = "User"
        user.job_title = "Суперадминистратор"
        user.role = 0.0
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        self.stdout.write(
            self.style.SUCCESS(
                f'{"Создан" if created else "Обновлён"} пользователь admin (пароль: admin).'
            )
        )
