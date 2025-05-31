from django.contrib import admin
from django.db import models

from altered.models import Deck, DeckVersion, Champion


class Game(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.PROTECT, related_name='games')
    deck_version = models.ForeignKey(DeckVersion, on_delete=models.PROTECT, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_win = models.BooleanField()
    opponent_champion = models.ForeignKey(Champion, on_delete=models.PROTECT)

    def __str__(self):
        result = "WIN" if self.is_win else "LOST"
        return f"{self.deck.name} vs {self.opponent_champion} ({result})"

    def save(self, *args, **kwargs):
        self.set_deck_version()
        super().save(*args, **kwargs)

    def set_deck_version(self):
        if self.deck_version is not None:
            return
        self.deck_version = self.deck.latest_version


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('deck', 'opponent_champion', 'is_win')
    list_filter = ('is_win',)
    ordering = ('-created_at',)
