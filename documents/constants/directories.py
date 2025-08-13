from django.db import models


class Directories(models.TextChoices):
    BACK_TO_THE_DAWN = "bttd", "Back to the Dawn"
    CIVILIZATION7 = "civ7", "Civilization 7"
    ALTERED = "alte", "Altered"
    RUNETERRA = "rune", "Runeterra"
    BAZAAR = "baza", "Bazaar"
