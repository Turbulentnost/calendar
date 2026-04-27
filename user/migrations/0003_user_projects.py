from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("calendarfunc", "0001_initial"),
        ("user", "0002_user_department"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="projects",
            field=models.ManyToManyField(
                blank=True,
                related_name="users",
                to="calendarfunc.project",
                verbose_name="Проекты",
            ),
        ),
    ]
