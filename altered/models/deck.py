from django.contrib import admin
from django.db import models

from altered.models import Champion


class Deck(models.Model):
    name = models.CharField(
        max_length=32,
    )
    champion = models.ForeignKey(Champion, on_delete=models.PROTECT, related_name='decks')
    altered_id = models.CharField(max_length=32)

    @property
    def latest_version(self):
        return self.versions.order_by('-created_at').first()

    def __str__(self):
        return f"{self.name} ({self.champion})"

    @property
    def faction(self):
        return self.champion.faction


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'champion',)
    list_filter = ('champion',)
    ordering = ('name',)
