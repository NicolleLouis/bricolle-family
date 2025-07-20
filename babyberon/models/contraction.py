from django.contrib import admin
from django.db import models


class Contraction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    power = models.PositiveSmallIntegerField(choices=[(1, "Petite"), (2, "Moyenne"), (3, "Forte")])


@admin.register(Contraction)
class ContractionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "power")
    ordering = ("-created_at",)
