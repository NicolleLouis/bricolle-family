from django.db import models


class Victory(models.TextChoices):
    CULTURE = "CULTURE", "Culture"
    SCIENCE = "SCIENCE", "Scientifique"
    COMMERCIAL = "COMMERCIAL", "Commerciale"
    MILITARY = "MILITARY", "Militaire"
