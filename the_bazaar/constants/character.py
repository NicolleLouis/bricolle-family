from django.db import models


class Character(models.TextChoices):
    DOOLEY = "DOOLEY", "Dooley"
    MAK = "MAK", "Mak"
    PYGMALIEN = "PYGMALIEN", "Pygmalien"
    STELLE = "STELLE", "Stelle"
    VANESSA = "VANESSA", "Vanessa"
