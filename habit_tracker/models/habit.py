from django.db import models


class Habit(models.Model):
    name = models.CharField(max_length=255)
    objective = models.ForeignKey(
        "habit_tracker.Objective",
        on_delete=models.SET_NULL,
        related_name="habits",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
