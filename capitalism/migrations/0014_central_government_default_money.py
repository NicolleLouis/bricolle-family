from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("capitalism", "0013_central_government"),
    ]

    operations = [
        migrations.AlterField(
            model_name="centralgovernment",
            name="money",
            field=models.FloatField(default=0.0),
        ),
    ]
