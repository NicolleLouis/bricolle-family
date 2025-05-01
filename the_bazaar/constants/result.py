from django.db import models


class Result(models.TextChoices):
    LOSS = "LOSS", "Loss"
    BRONZE_WIN = "BRONZE_WIN", "Bronze win"
    SILVER_WIN = "SILVER_WIN", "Silver win"
    GOLD_WIN = "GOLD_WIN", "Gold win"
