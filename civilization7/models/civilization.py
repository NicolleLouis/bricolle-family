from django.contrib import admin
from django.db import models

from civilization7.constants.epoque import Epoque


class Civilization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    epoque = models.CharField(max_length=20, choices=Epoque.choices)

    def __str__(self):
        return self.name


@admin.register(Civilization)
class CivilizationAdmin(admin.ModelAdmin):
    list_display = ("name", "epoque")
    list_filter = ("epoque",)
    search_fields = ("name",)
