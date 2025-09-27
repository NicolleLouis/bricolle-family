from django.contrib import admin
from django.db import models


class PitStop(models.Model):
    start_date = models.DateTimeField()
    quantity = models.IntegerField(help_text="in mL")
    comment = models.TextField(blank=True)
    delay_before_next_pit_stop = models.IntegerField(
        null=True, blank=True, help_text="in min"
    )


@admin.register(PitStop)
class PitStopAdmin(admin.ModelAdmin):
    list_display = ("start_date", "quantity", "delay_before_next_pit_stop", "comment")
    ordering = ("-start_date",)
