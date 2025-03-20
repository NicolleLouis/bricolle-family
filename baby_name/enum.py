from django.db import models

class NameChoice(models.TextChoices):
    OUI = "oui", "Oui"
    NON = "non", "Non"
    COUP_DE_COEUR = "coup_de_coeur", "Coup de cœur"
