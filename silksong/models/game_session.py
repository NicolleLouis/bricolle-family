from django.db import models

from silksong.constants import Boss, GameSessionType
from silksong.constants.death_explanation import DEATH_EXPLANATION_CHOICES


class GameSession(models.Model):
    type = models.CharField(max_length=32, choices=GameSessionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    boss = models.CharField(
        max_length=50,
        choices=Boss.choices,
        null=True,
        blank=True,
    )
    duration = models.PositiveIntegerField(null=True, blank=True)
    death_number = models.PositiveIntegerField(null=True, blank=True)
    death_explanation = models.CharField(
        max_length=50,
        choices=DEATH_EXPLANATION_CHOICES,
        null=True,
        blank=True,
    )
    victory = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.get_type_display()} - {self.created_at:%Y-%m-%d %H:%M}"
