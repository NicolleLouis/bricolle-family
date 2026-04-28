from datetime import timedelta

from django.contrib import admin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.models.object import Object


class Price(models.Model):
    sell_price_min = models.PositiveIntegerField()
    sell_price_min_date = models.DateTimeField(db_index=True)
    sell_price_max = models.PositiveIntegerField(null=True, blank=True)
    sell_price_max_date = models.DateTimeField(null=True, blank=True)
    buy_price_min = models.PositiveIntegerField(null=True, blank=True)
    buy_price_min_date = models.DateTimeField(null=True, blank=True)
    buy_price_max = models.PositiveIntegerField(null=True, blank=True)
    buy_price_max_date = models.DateTimeField(null=True, blank=True)
    city = models.CharField(max_length=16, choices=City.choices, db_index=True)
    object = models.ForeignKey(
        Object,
        on_delete=models.CASCADE,
        related_name="prices",
    )
    quality = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        db_index=True,
    )

    class Meta:
        ordering = ("-sell_price_min_date", "city", "object_id", "quality")
        indexes = [
            models.Index(fields=("object", "city", "quality", "-sell_price_min_date")),
        ]

    def __str__(self):
        return f"{self.object.aodp_id} - {self.city} - Q{self.quality} - {self.sell_price_min}"

    @property
    def price(self):
        return self.sell_price_min

    @property
    def timestamp(self):
        return self.sell_price_min_date

    @property
    def sell_price(self):
        return self.sell_price_min

    @property
    def buy_price(self):
        return self.buy_price_max

    @staticmethod
    def build_freshness(timestamp):
        if timestamp is None:
            return {
                "label": "Info indisponible",
                "class_name": "bg-secondary",
            }

        age = timezone.now() - timestamp
        if age > timedelta(days=1):
            return {
                "label": "Info > 1 jour",
                "class_name": "bg-danger",
            }
        if age > timedelta(hours=1):
            return {
                "label": "Info > 1 heure",
                "class_name": "bg-warning text-dark",
            }
        return {
            "label": "Info fiable",
            "class_name": "bg-success",
        }

    @property
    def sell_price_freshness(self):
        return self.build_freshness(self.sell_price_min_date)

    @property
    def buy_price_freshness(self):
        return self.build_freshness(self.buy_price_max_date)


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = (
        "object",
        "city",
        "quality",
        "sell_price_min",
        "sell_price_max",
        "buy_price_min",
        "buy_price_max",
        "sell_price_min_date",
    )
    list_filter = ("city", "quality", "sell_price_min_date")
    search_fields = ("object__aodp_id", "object__name")
    autocomplete_fields = ("object",)
    ordering = ("-sell_price_min_date", "city", "object", "quality")
