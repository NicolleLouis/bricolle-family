from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("capitalism", "0004_alter_human_money"),
    ]

    operations = [
        migrations.AlterField(
            model_name="human",
            name="money",
            field=models.FloatField(default=150.0),
        ),
    ]
