from django.contrib import admin
from django.db import models


class Contraction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    power = models.PositiveSmallIntegerField(choices=[(1, "Small"), (2, "Medium"), (3, "Strong")])


@admin.register(Contraction)
class ContractionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "power")
    ordering = ("-created_at",)
