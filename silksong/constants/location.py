from django.db import models


class Location(models.TextChoices):
    MOSS = "Moss", "Moss"
    DEEP_WORK = "Deep work", "Deep work"
