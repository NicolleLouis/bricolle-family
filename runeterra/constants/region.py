from django.db import models


class Region(models.TextChoices):
    TARGON = "TARGON", "Targon"
    RUNETERRA = "RUNETERRA", "Runeterra"
    DEMACIA = "DEMACIA", "Demacia"
    NOXUS = "NOXUS", "Noxus"
    IONIA = "IONIA", "Ionia"
    BUNDLE = "BUNDLE", "Bundle"
    PILTOVER_ZAUN = "PILTOVER_ZAUN", "Piltover & Zaun"
    BILGEWATER = "BILGEWATER", "Bilgewater"
