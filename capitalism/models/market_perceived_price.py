from django.contrib import admin
from django.db import models

from capitalism.constants.object_type import ObjectType


class MarketPerceivedPrice(models.Model):
    updated_at = models.IntegerField()
    perceived_price = models.FloatField()
    object = models.CharField(
        max_length=32,
        choices=ObjectType.choices,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("object",),
                name="market_perceived_price_unique_object",
            )
        ]

    def __str__(self):
        return f"{self.get_object_display()} perception on day {self.updated_at}"


@admin.register(MarketPerceivedPrice)
class MarketPerceivedPriceAdmin(admin.ModelAdmin):
    list_display = ("id", "updated_at", "object", "perceived_price")
    list_filter = ("object",)
    search_fields = ("object",)
