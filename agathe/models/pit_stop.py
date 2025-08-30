from django.contrib import admin
from django.db import models


class PitStop(models.Model):
    class Side(models.TextChoices):
        LEFT = "L", "Gauche"
        RIGHT = "R", "Droit"

    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    side = models.CharField(max_length=1, choices=Side.choices)

    @property
    def ongoing(self):
        return self.end_date is None

    @property
    def duration(self):
        if self.end_date is None:
            return None
        delta = self.end_date - self.start_date
        return delta.total_seconds() / 60


@admin.register(PitStop)
class PitStopAdmin(admin.ModelAdmin):
    list_display = ("start_date", "end_date", "side")
    ordering = ("-start_date",)
