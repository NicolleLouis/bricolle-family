from django.db import models


class Day(models.Model):
    date = models.DateField(unique=True)
    habits = models.ManyToManyField("habit_tracker.Habit", related_name="days", blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:
        return self.date.isoformat()
