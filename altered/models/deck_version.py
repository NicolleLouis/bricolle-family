from django.contrib import admin
from django.db import models

from altered.models import Deck


class DeckVersion(models.Model):
    version_number = models.IntegerField()
    deck = models.ForeignKey(Deck, on_delete=models.PROTECT, related_name='versions')
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.deck} ({self.version_number})"


@admin.register(DeckVersion)
class DeckVersionAdmin(admin.ModelAdmin):
    list_display = ('deck', 'version_number',)
    list_filter = ('deck',)
    ordering = ('version_number',)
