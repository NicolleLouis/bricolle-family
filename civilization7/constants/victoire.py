from django.db import models


class Victoire(models.TextChoices):
    CULTURE = "CULTURE", "Culture"
    SCIENTIFIQUE = "SCIENTIFIQUE", "Scientifique"
    COMMERCIALE = "COMMERCIALE", "Commerciale"
    MILITAIRE = "MILITAIRE", "Militaire"
