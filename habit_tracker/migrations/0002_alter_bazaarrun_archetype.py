# Generated by Django 4.2.20 on 2025-04-09 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habit_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bazaarrun',
            name='archetype',
            field=models.CharField(blank=True, choices=[('FIXER_UPPER', 'Fixer Upper')], max_length=11, null=True),
        ),
    ]
