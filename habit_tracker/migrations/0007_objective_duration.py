from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("habit_tracker", "0006_objective_check_frequency"),
    ]

    operations = [
        migrations.AddField(
            model_name="objective",
            name="objective_duration",
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
