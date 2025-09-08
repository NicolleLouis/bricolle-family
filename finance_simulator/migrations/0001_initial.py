# Generated manually for Simulation model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Simulation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('house_cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('initial_contribution', models.DecimalField(decimal_places=2, max_digits=12)),
                ('duration', models.IntegerField()),
                ('annual_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('comparative_rent', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('duration_before_usable', models.IntegerField(blank=True, null=True)),
                ('use_real_estate_firm', models.BooleanField(default=True)),
                ('sell_price_change', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
