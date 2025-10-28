from django.db import models


class Job(models.TextChoices):
    MINER = "miner", "Miner"
    LUMBERJACK = "lumberjack", "Lumberjack"
    TOOLMAKER = "toolmaker", "Tool Maker"
    FARMER = "farmer", "Farmer"
    MILLER = "miller", "Miller"
    BAKER = "baker", "Baker"
