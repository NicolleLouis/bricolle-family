from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sport", "0003_session"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrainingTarget",
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
                ("name", models.CharField(max_length=150, unique=True)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
    ]
