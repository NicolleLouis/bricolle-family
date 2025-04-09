from django.db import models


class Character(models.TextChoices):
    DOOLEY = "DOOLEY", "Dooley"
    MAK = "MAK", "Mak"
    PYGMALIEN = "PYGMALIEN", "Pygmalien"
    VANESSA = "VANESSA", "Vanessa"
