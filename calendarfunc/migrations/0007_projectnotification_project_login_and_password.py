from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calendarfunc", "0006_projectnotification"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectnotification",
            name="project_login",
            field=models.CharField(blank=True, max_length=150, verbose_name="Логин проекта в приглашении"),
        ),
        migrations.AddField(
            model_name="projectnotification",
            name="project_password",
            field=models.CharField(blank=True, max_length=255, verbose_name="Пароль проекта в приглашении"),
        ),
    ]
