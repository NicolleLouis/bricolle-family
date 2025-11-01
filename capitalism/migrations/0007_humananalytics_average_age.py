from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("capitalism", "0006_humananalytics_dead_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="humananalytics",
            name="average_age",
            field=models.FloatField(default=0.0),
        ),
    ]
