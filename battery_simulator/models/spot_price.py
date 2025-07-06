from django.contrib import admin
from django.db import models


class SpotPrice(models.Model):
    date = models.DateTimeField()
    price = models.FloatField(help_text="€/MWh")

    def __str__(self):
        return f"{self.date.strftime('%d/%m/%Y %HH')} ({self.price}€/MWh)"


@admin.register(SpotPrice)
class SpotPriceAdmin(admin.ModelAdmin):
    list_display = ('price', 'formatted_date')
    ordering = ('-date',)

    @admin.display(description='Created At')
    def formatted_date(self, obj):
        return obj.date.strftime('%d/%m/%Y %H')
