# Generated by Django 4.2.20 on 2025-04-10 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('habit_tracker', '0005_alter_bazaarrun_archetype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bazaarrun',
            name='archetype',
        ),
    ]
