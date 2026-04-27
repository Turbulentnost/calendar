from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="department",
            field=models.CharField(blank=True, max_length=255, verbose_name="Отдел"),
        ),
    ]
