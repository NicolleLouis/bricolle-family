from django.db import models


class EquipmentCategory(models.TextChoices):
    CHEST = "CHEST", "Chest"
    OFFHAND = "OFFHAND", "Offhand"
    SINGLE_HAND = "SINGLE_HAND", "Single Hand"
    TWO_HAND = "TWO_HAND", "Two-Hand"
    SHOE = "SHOE", "Shoe"
