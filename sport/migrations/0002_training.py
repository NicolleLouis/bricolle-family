from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sport", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Training",
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
                ("name", models.CharField(max_length=150)),
                ("content", models.TextField(blank=True, help_text="Markdown content")),
            ],
        ),
        migrations.AddField(
            model_name="training",
            name="training_types",
            field=models.ManyToManyField(
                blank=True, related_name="trainings", to="sport.trainingtype"
            ),
        ),
    ]
