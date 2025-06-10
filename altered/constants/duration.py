from django.db import models


class Duration(models.TextChoices):
    ALL = "ALL", "All time"
    LAST_6_MONTHS = "6_MONTHS", "Last 6 months"
    LAST_3_MONTHS = "3_MONTHS", "Last 3 months"
    LAST_MONTH = "1_MONTH", "Last month"
