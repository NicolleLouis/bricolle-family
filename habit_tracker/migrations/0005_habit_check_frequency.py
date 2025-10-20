from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("habit_tracker", "0004_auto_assign_objectives_to_habits"),
    ]

    operations = [
        migrations.AddField(
            model_name="habit",
            name="check_frequency",
            field=models.CharField(
                choices=[("daily", "Journalier"), ("weekly", "Hebdomadaire")],
                default="daily",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="habit",
            name="objective_in_frequency",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddConstraint(
            model_name="habit",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(
                        check_frequency="daily",
                        objective_in_frequency=1,
                    )
                    | (
                        models.Q(check_frequency="weekly")
                        & models.Q(objective_in_frequency__gte=1)
                        & models.Q(objective_in_frequency__lte=6)
                    )
                ),
                name="habit_objective_freq_daily_or_weekly",
            ),
        ),
    ]
