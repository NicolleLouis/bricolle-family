from django.contrib import admin
from django.db import models

from capitalism.constants.jobs import Job


class HumanAnalytics(models.Model):
    job = models.CharField(
        max_length=32,
        choices=Job.choices,
        default=Job.MINER,
    )
    day_number = models.IntegerField(default=0)
    number_alive = models.IntegerField(default=0)
    average_money = models.FloatField(default=0.0)
    lowest_money = models.IntegerField(default=0)
    max_money = models.IntegerField(default=0)
    new_joiner = models.IntegerField(default=0)
    dead_number = models.IntegerField(default=0)
    average_age = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.get_job_display()} analytics for day {self.day_number}"


@admin.register(HumanAnalytics)
class HumanAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job",
        "day_number",
        "number_alive",
        "average_money",
        "lowest_money",
        "max_money",
        "new_joiner",
        "dead_number",
        "average_age",
    )
    list_filter = ("job",)
