from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("habit_tracker", "0005_habit_check_frequency"),
    ]

    operations = [
        migrations.AddField(
            model_name="objective",
            name="check_frequency",
            field=models.CharField(
                choices=[("daily", "Journalier"), ("weekly", "Hebdomadaire")],
                default="weekly",
                max_length=16,
            ),
        ),
    ]
