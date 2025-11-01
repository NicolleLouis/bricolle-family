from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("capitalism", "0007_humananalytics_average_age"),
    ]

    operations = [
        migrations.AddField(
            model_name="priceanalytics",
            name="transaction_number",
            field=models.IntegerField(default=0),
        ),
    ]
