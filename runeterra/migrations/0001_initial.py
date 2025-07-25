# Generated by Django 4.2.20 on 2025-07-13 14:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Champion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "region",
                    models.CharField(
                        choices=[
                            ("TARGON", "Targon"),
                            ("RUNETERRA", "Runeterra"),
                            ("DEMACIA", "Demacia"),
                            ("NOXUS", "Noxus"),
                            ("IONIA", "Ionia"),
                            ("BUNDLE", "Bundle"),
                            ("PILTOVER_ZAUN", "Piltover & Zaun"),
                            ("BILGEWATER", "Bilgewater"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "star_level",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(6),
                        ]
                    ),
                ),
                ("unlocked", models.BooleanField(default=False)),
                ("lvl30", models.BooleanField(default=False)),
            ],
        ),
    ]
