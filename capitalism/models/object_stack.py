from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.contrib import admin
from django.db import models

from capitalism.constants.object_type import ObjectType
from .human import Human


class ObjectStackQuerySet(models.QuerySet):
    def total_quantity(self) -> int:
        total = self.aggregate(total=models.Sum("quantity"))["total"]
        return int(total or 0)


class ObjectStack(models.Model):
    owner = models.ForeignKey(Human, on_delete=models.CASCADE, related_name="owned_objects")
    in_sale = models.BooleanField(default=False)
    price = models.FloatField(null=True, blank=True, default=None)
    type = models.CharField(
        max_length=32,
        choices=ObjectType.choices,
        default=ObjectType.BREAD,
    )
    quantity = models.PositiveIntegerField(default=1)

    objects = ObjectStackQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if self.price is not None:
            decimal_price = Decimal(str(self.price)).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
            self.price = float(decimal_price)
        super().save(*args, **kwargs)

    def __str__(self):
        label = self.get_type_display()
        return f"{self.quantity}x {label} for {self.owner}"


@admin.register(ObjectStack)
class ObjectStackAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "type", "quantity", "in_sale", "price")
    list_filter = ("type", "in_sale")
    search_fields = ("owner__id", "type")
