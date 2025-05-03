from django.db import models


class BuildOrderMilestoneType(models.TextChoices):
    BUILDING = "BUILDING", "Building"
    TECHNOLOGY = "TECHNOLOGY", "Technology"
