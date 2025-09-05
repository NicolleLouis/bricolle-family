from django.db import models


class Epoque(models.TextChoices):
    ANTIQUITE = "ANTIQUITE", "Antiquité"
    EXPLORATION = "EXPLORATION", "Exploration"
    MODERNE = "MODERNE", "Moderne"
