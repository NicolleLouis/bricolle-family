from django.db import models
from django.contrib import admin


class UniqueFlip(models.Model):
    unique_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128, null=True, blank=True)
    image_path = models.CharField(max_length=256, null=True, blank=True)
    bought_at = models.DateTimeField()
    bought_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_at = models.DateTimeField(null=True, blank=True)
    sold_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.unique_id

    @property
    def balance(self):
        sold = self.sold_price or 0
        return sold - self.bought_price


@admin.register(UniqueFlip)
class UniqueFlipAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'name', 'bought_at', 'bought_price', 'sold_at', 'sold_price')
    list_filter = ('sold_at',)
    ordering = ('-bought_at',)
