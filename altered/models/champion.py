from django.contrib import admin
from django.db import models

from altered.constants.faction import Faction


class Champion(models.Model):
    name = models.CharField(
        max_length=32,
    )
    faction = models.CharField(
        max_length=8,
        choices=Faction.choices,
    )

    def __str__(self):
        return f"{self.name} ({self.faction})"


@admin.register(Champion)
class ChampionAdmin(admin.ModelAdmin):
    list_display = ('name', 'faction',)
    list_filter = ('faction',)
    ordering = ('name',)
