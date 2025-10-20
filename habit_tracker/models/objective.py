from django.db import models

from .choices import CheckFrequency


class Objective(models.Model):
    name = models.CharField(max_length=255)
    check_frequency = models.CharField(
        max_length=16,
        choices=CheckFrequency.choices,
        default=CheckFrequency.WEEKLY,
    )
    objective_duration = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
