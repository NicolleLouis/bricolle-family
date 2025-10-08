from django.contrib import admin
from django.db import models

from altered.constants.card import CardExtension, CardRarity
from altered.constants.faction import Faction


class Card(models.Model):
    name = models.CharField(max_length=255)
    extension = models.CharField(max_length=32, choices=CardExtension.choices)
    hand_cost = models.PositiveIntegerField()
    reserve_cost = models.PositiveIntegerField()
    faction = models.CharField(max_length=8, choices=Faction.choices)
    forest_amount = models.PositiveIntegerField(default=0)
    water_amount = models.PositiveIntegerField(default=0)
    mountain_amount = models.PositiveIntegerField(default=0)
    effects = models.JSONField(default=list, blank=True)
    rarity = models.CharField(max_length=16, choices=CardRarity.choices)
    altered_id = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ("name", "extension")

    def __str__(self):
        return f"{self.name} ({self.get_extension_display()})"


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("name", "extension", "rarity", "faction", "altered_id")
    list_filter = ("extension", "rarity", "faction")
    search_fields = ("name", "altered_id")
    ordering = ("name",)
