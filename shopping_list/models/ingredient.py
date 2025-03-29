from django.contrib import admin
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=32)
    is_pantry_staples = models.BooleanField()
    unit = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} (par: {self.unit})"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_pantry_staples')
    list_filter = ('is_pantry_staples',)
    search_fields = ["name"]
    ordering = ('name',)
