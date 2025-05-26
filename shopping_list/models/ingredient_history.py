from django.contrib import admin
from django.db import models

from shopping_list.models.ingredient import Ingredient

class IngredientHistory(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    bought_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ingredient.name} - {self.quantity} on {self.bought_date.strftime('%Y-%m-%d')}"

@admin.register(IngredientHistory)
class IngredientHistoryAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'quantity', 'formatted_bought_date')
    search_fields = ['ingredient__name']
    list_filter = ['ingredient', 'bought_date']
    ordering = ('-bought_date',)

    @admin.display(description='Bought Date', ordering='bought_date')
    def formatted_bought_date(self, obj):
        return obj.bought_date.strftime('%d/%m/%Y %H:%M')
