from django.db import models


class Directories(models.TextChoices):
    AGATHE = "agathe", "Agathe"
    ALTERED = "altered", "Altered"
    BACK_TO_THE_DAWN = "bttd", "Back to the Dawn"
    BAZAAR = "bazaar", "The Bazaar"
    CIVILIZATION7 = "civilization_7", "Civilization 7"
    FINANCE_SIMULATOR = "finance", "Finance Simulator"
    SILKSONG = "silksong", "Silksong"
    RUNETERRA = "runeterra", "Runeterra"
    SPEEDRUN = "speedrun", "Speedrun"
    SPORT = "sport", "Sport"
