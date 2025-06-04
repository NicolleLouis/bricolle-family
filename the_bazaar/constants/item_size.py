from django.db import models


class ItemSize(models.TextChoices):
    SMALL = "SMALL", "Small"
    MEDIUM = "MEDIUM", "Medium"
    LARGE = "LARGE", "Large"

