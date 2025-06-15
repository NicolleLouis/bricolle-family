from django.contrib import admin
from django.db import models

from chess.constants.training_type import TrainingType


class TrainingSession(models.Model):
    training_type = models.CharField(
        max_length=10,
        choices=TrainingType.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)
    elo = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_training_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ("training_type", "elo", "created_at")
    list_filter = ("training_type",)
    ordering = ("-created_at",)
