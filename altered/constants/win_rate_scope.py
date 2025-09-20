from django.db import models


class WinRateScope(models.TextChoices):
    ALL = "all", "Tous les matchs"
    FACTION = "faction", "Par faction"
    CHAMPION = "champion", "Par champion"
    DECK = "deck", "Par deck"
