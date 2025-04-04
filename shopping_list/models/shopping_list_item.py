from django.contrib import admin
from django.db import models


class ShoppingListItem(models.Model):
    ingredient = models.ForeignKey('shopping_list.Ingredient', related_name='wanted_items', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} {self.ingredient.name}"

    class Meta:
        permissions = [
            ("shopping_list_access", "Can access shopping list module")
        ]


class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'quantity')
    list_filter = ('ingredient__name',)
    search_fields = ['ingredient__name']
    ordering = ('ingredient',)
