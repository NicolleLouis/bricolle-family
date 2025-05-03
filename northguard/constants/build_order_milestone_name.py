from django.db import models


class BuildOrderMilestoneName(models.TextChoices):
    SCOUT = "SCOUT", "Scout"
    LUMBERJACK = "LUMBERJACK", "Lumberjack"
