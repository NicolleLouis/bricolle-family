from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('altered', '0018_remove_deckversion_cards'),
    ]

    operations = [
        migrations.AddField(
            model_name='uniqueflip',
            name='advised_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
