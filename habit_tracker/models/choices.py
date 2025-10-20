from django.db import models


class CheckFrequency(models.TextChoices):
    DAILY = "daily", "Journalier"
    WEEKLY = "weekly", "Hebdomadaire"

