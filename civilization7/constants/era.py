from django.db import models


class Era(models.TextChoices):
    ANCIENT = "ANCIENT", "Antiquité"
    EXPLORATION = "EXPLORATION", "Exploration"
    MODERN = "MODERN", "Moderne"
