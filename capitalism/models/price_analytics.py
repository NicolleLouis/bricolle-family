from django.contrib import admin
from django.db import models

from capitalism.constants.object_type import ObjectType


class PriceAnalytics(models.Model):
    day_number = models.IntegerField()
    object_type = models.CharField(
        max_length=32,
        choices=ObjectType.choices,
    )
    lowest_price_displayed = models.FloatField()
    max_price_displayed = models.FloatField()
    average_price_displayed = models.FloatField()
    lowest_price = models.FloatField()
    max_price = models.FloatField()
    average_price = models.FloatField()

    class Meta:
        unique_together = ("day_number", "object_type")

    def __str__(self):
        return f"{self.get_object_type_display()} - Day {self.day_number}"


@admin.register(PriceAnalytics)
class PriceAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "day_number",
        "object_type",
        "lowest_price_displayed",
        "max_price_displayed",
        "average_price_displayed",
        "lowest_price",
        "max_price",
        "average_price",
    )
    list_filter = ("object_type",)
    search_fields = ("object_type",)
