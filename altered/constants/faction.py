from django.db import models


class Faction(models.TextChoices):
    AXIOM = "AXIOM", "Axiom"
    BRAVOS = "BRAVOS", "Bravos"
    LYRA = "LYRA", "Lyra"
    MUNA = "MUNA", "Muna"
    ORDIS = "ORDIS", "Ordis"
    YZMIR = "YZMIR", "Yzmir"
