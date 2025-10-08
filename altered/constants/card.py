from django.db import models


class CardExtension(models.TextChoices):
    BEYONG_THE_GATE = "BEYONG_THE_GATE", "Beyong the gate"
    TRIAL_BY_FROST = "TRIAL_BY_FROST", "Trial by frost"
    WHISPERS_FROM_THE_MAZE = "WHISPERS_FROM_THE_MAZE", "Whispers from the maze"
    SKYBOUND_ODYSSEY = "SKYBOUND_ODYSSEY", "Skybound Odyssey"


class CardRarity(models.TextChoices):
    COMMON = "COMMON", "Commun"
    RARE = "RARE", "Rare"
    UNIQUE = "UNIQUE", "Unique"
