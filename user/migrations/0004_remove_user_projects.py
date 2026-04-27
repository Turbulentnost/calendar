from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0003_user_projects"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="projects",
        ),
    ]
