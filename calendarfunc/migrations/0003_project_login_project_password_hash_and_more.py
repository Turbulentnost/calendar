from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("calendarfunc", "0002_projecttask"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="login",
            field=models.CharField(blank=True, max_length=150, null=True, unique=True, verbose_name="Логин проекта"),
        ),
        migrations.AddField(
            model_name="project",
            name="password_hash",
            field=models.CharField(blank=True, max_length=128, verbose_name="Пароль проекта"),
        ),
        migrations.AddField(
            model_name="projecttask",
            name="is_carried_over",
            field=models.BooleanField(default=False, verbose_name="Перенесена"),
        ),
        migrations.AddField(
            model_name="projecttask",
            name="is_closed",
            field=models.BooleanField(default=False, verbose_name="Закрыта"),
        ),
        migrations.DeleteModel(
            name="ProjectInvitation",
        ),
    ]
