from django.contrib import admin
from django.db import models

from civilization7.constants.era import Era


class Wonder(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nom")
    era = models.CharField(max_length=20, choices=Era.choices, verbose_name="Époque")

    def __str__(self):
        return self.name


@admin.register(Wonder)
class WonderAdmin(admin.ModelAdmin):
    list_display = ("name", "era")
    list_filter = ("era",)
    search_fields = ("name",)
