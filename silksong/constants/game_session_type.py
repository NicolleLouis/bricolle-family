from django.db import models


class GameSessionType(models.TextChoices):
    SPEEDRUN = "speedrun", "Speedrun"
    STEEL_SOUL = "steel_soul", "Steel Soul"
    BOSS_FIGHT = "boss_fight", "Boss Fight"
