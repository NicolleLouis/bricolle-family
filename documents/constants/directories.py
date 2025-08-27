from django.db import models


class Directories(models.TextChoices):
    BACK_TO_THE_DAWN = "bttd", "Back to the Dawn"
    CIVILIZATION7 = "civilization_7", "Civilization 7"
    ALTERED = "altered", "Altered"
    RUNETERRA = "runeterra", "Runeterra"
    BAZAAR = "bazaar", "The Bazaar"
    AGATHER = "agather", "Agather"
