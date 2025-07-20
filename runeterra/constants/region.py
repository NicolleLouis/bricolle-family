from django.db import models


class Region(models.TextChoices):
    BANDLE = "BANDLE", "Bandle"
    BILGEWATER = "BILGEWATER", "Bilgewater"
    DEMACIA = "DEMACIA", "Demacia"
    FRELJORD = "FRELJORD", "Freljord"
    IONIA = "IONIA", "Ionia"
    NOXUS = "NOXUS", "Noxus"
    PILTOVER_ZAUN = "PILTOVER_ZAUN", "Piltover & Zaun"
    RUNETERRA = "RUNETERRA", "Runeterra"
    SHADOW_ISLES = "SHADOW_ISLES", "Shadow Isles"
    SHURIMA = "SHURIMA", "Shurima"
    TARGON = "TARGON", "Targon"
