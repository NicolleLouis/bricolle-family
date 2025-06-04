from django.contrib import admin
from django.db import models


class DeckVersion(models.Model):
    version_number = models.IntegerField()
    deck = models.ForeignKey('altered.Deck', on_delete=models.PROTECT, related_name='versions')
    content = models.TextField(null=True, blank=True)
    change_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.deck.name} (v{self.version_number})"


@admin.register(DeckVersion)
class DeckVersionAdmin(admin.ModelAdmin):
    list_display = ('deck', 'version_number', 'change_cost')
    list_filter = ('deck',)
    ordering = ('version_number',)
