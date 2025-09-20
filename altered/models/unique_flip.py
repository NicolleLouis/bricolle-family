from decimal import Decimal

from django.db import models
from django.contrib import admin

from altered.constants.faction import Faction


class UniqueFlip(models.Model):
    unique_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128, null=True, blank=True)
    image_path = models.CharField(max_length=256, null=True, blank=True)
    faction = models.CharField(
        max_length=8,
        choices=Faction.choices,
        null=True,
        blank=True,
    )
    main_cost = models.IntegerField(null=True, blank=True)
    recall_cost = models.IntegerField(null=True, blank=True)
    mountain_power = models.IntegerField(null=True, blank=True)
    ocean_power = models.IntegerField(null=True, blank=True)
    forest_power = models.IntegerField(null=True, blank=True)
    bought_at = models.DateTimeField()
    bought_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_at = models.DateTimeField(null=True, blank=True)
    sold_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    in_use = models.BooleanField(default=False)

    def __str__(self):
        return self.unique_id

    @property
    def balance(self):
        sold = self.sold_price or 0
        return round((sold * Decimal('0.95')) - self.bought_price, 2)

    @property
    def balance_percentage(self):
        if self.bought_price == 0:
            return None
        return (self.balance / self.bought_price) * 100


@admin.register(UniqueFlip)
class UniqueFlipAdmin(admin.ModelAdmin):
    list_display = (
        'unique_id',
        'name',
        'bought_at',
        'bought_price',
        'sold_at',
        'sold_price',
        'in_use',
    )
    list_filter = ('sold_at',)
    ordering = ('-bought_at',)
