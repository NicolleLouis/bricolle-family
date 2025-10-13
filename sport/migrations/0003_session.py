from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sport", "0002_training"),
    ]

    operations = [
        migrations.CreateModel(
            name="Session",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                (
                    "training",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="sessions",
                        to="sport.training",
                    ),
                ),
            ],
        ),
    ]
