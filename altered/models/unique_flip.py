from decimal import Decimal
from django.utils import timezone

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
    advised_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    in_use = models.BooleanField(default=False)

    def __str__(self):
        if self.sold_price is None:
            return f"{self.unique_id} bought at: {self.bought_price}"
        return f"{self.unique_id} sold with balance: {self.balance}"

    @property
    def balance(self):
        sold = self.sold_price or 0
        return round((sold * Decimal('0.95')) - self.bought_price, 2)

    @property
    def balance_percentage(self):
        if self.bought_price == 0:
            return None
        return (self.balance / self.bought_price) * 100

    @property
    def is_sold(self):
        return self.sold_price is not None

    @property
    def current_price(self):
        prices = self.prices.all()
        if prices.exists():
            return prices.first().price
        return None

    def save_price(self, price):
        from altered.models.unique_price import UniquePrice

        current = self.current_price

        if current == price:
            return

        self.advised_price = None
        self.save(update_fields=['advised_price'])

        UniquePrice.objects.create(
            date=timezone.now(),
            price=price,
            unique_flip=self
        )


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
