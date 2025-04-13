from django.contrib import admin
from django.db import models

from shopping_list.constants.category import Category


class Ingredient(models.Model):
    name = models.CharField(max_length=32, unique=True)
    is_pantry_staples = models.BooleanField()
    unit = models.CharField(max_length=20)
    category = models.CharField(
        max_length=12,
        choices=Category.choices,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} (par: {self.unit})"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_pantry_staples')
    list_filter = ('is_pantry_staples', 'category',)
    search_fields = ["name"]
    ordering = ('name',)
