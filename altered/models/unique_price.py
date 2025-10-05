from django.contrib import admin
from django.db import models

from altered.models.unique_flip import UniqueFlip


class UniquePrice(models.Model):
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unique_flip = models.ForeignKey(
        UniqueFlip,
        on_delete=models.CASCADE,
        related_name='prices'
    )

    def __str__(self):
        return f"{self.date.strftime('%d/%m/%Y')} - {self.price}€ - {self.unique_flip}"

    class Meta:
        ordering = ['-date']


@admin.register(UniquePrice)
class UniquePriceAdmin(admin.ModelAdmin):
    list_display = ('unique_flip', 'price', 'formatted_date')
    list_filter = ('unique_flip',)
    ordering = ('-date',)

    @admin.display(description='Date')
    def formatted_date(self, obj):
        return obj.date.strftime('%d/%m/%Y')