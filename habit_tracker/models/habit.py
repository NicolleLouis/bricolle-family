from django.core.exceptions import ValidationError
from django.db import models

from .choices import CheckFrequency


class Habit(models.Model):
    name = models.CharField(max_length=255)
    objective = models.ForeignKey(
        "habit_tracker.Objective",
        on_delete=models.SET_NULL,
        related_name="habits",
        null=True,
        blank=True,
    )
    check_frequency = models.CharField(
        max_length=16,
        choices=CheckFrequency.choices,
        default=CheckFrequency.DAILY,
    )
    objective_in_frequency = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                name="habit_objective_freq_daily_or_weekly",
                check=(
                    models.Q(
                        check_frequency=CheckFrequency.DAILY,
                        objective_in_frequency=1,
                    )
                    | (
                        models.Q(check_frequency=CheckFrequency.WEEKLY)
                        & models.Q(objective_in_frequency__gte=1)
                        & models.Q(objective_in_frequency__lte=6)
                    )
                ),
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if self.check_frequency == CheckFrequency.DAILY and self.objective_in_frequency != 1:
            raise ValidationError(
                {"objective_in_frequency": "Doit valoir 1 pour une fréquence journalière."}
            )
        if self.check_frequency == CheckFrequency.WEEKLY and not (
            1 <= self.objective_in_frequency <= 6
        ):
            raise ValidationError(
                {"objective_in_frequency": "Doit être compris entre 1 et 6 pour une fréquence hebdomadaire."}
            )
