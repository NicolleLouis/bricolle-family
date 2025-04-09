from django.db import models


class Archetype(models.TextChoices):
    FIXER_UPPER = "FIXER_UPPER", "Fixer Upper"
