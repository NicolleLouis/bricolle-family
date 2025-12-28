from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("capitalism", "0014_central_government_default_money"),
    ]

    operations = [
        migrations.AddField(
            model_name="centralgovernment",
            name="lifetime_collected_money",
            field=models.FloatField(default=0.0),
        ),
    ]
