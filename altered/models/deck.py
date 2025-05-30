from django.contrib import admin
from django.db import models

from altered.constants.faction import Faction
from altered.models import Champion


class Deck(models.Model):
    name = models.CharField(
        max_length=32,
    )
    faction = models.CharField(
        max_length=8,
        choices=Faction.choices,
    )
    champion = models.ForeignKey(Champion, on_delete=models.PROTECT, related_name='decks')
    altered_id = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name} ({self.champion})"


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'champion',)
    list_filter = ('faction',)
    ordering = ('name',)
