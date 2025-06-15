from django.db import models


class TrainingType(models.TextChoices):
    PUZZLE = "PUZZLE", "Puzzle"
    BLITZ = "BLITZ", "Blitz"
    TEN_MIN = "TEN_MIN", "10 min"
    BOOK = "BOOK", "Book"
