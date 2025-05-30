# Generated by Django 4.2.20 on 2025-05-04 08:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('northguard', '0003_buildordermilestone_alter_clan_name_buildorder'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildOrderStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('build_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='northguard.buildorder')),
                ('milestone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='northguard.buildordermilestone')),
            ],
            options={
                'unique_together': {('build_order', 'order')},
            },
        ),
    ]
