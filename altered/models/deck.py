from django.contrib import admin, messages
from django.db import models

from altered.models import Champion


class Deck(models.Model):
    name = models.CharField(
        max_length=32,
    )
    champion = models.ForeignKey(Champion, on_delete=models.PROTECT, related_name='decks')
    altered_id = models.CharField(max_length=32)

    is_active = models.BooleanField(default=True)

    @property
    def latest_version(self):
        return self.versions.order_by('-created_at').first()

    def __str__(self):
        return f"{self.name} ({self.champion.name})"

    @property
    def faction(self):
        return self.champion.faction


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'champion', 'is_active',)
    list_filter = ('champion', 'is_active',)
    ordering = ('name',)
    actions = ["update_version"]

    @admin.action(description="Update version")
    def update_version(self, request, queryset):
        from altered.services.altered_fetch_deck_data import AlteredFetchDeckDataService

        for deck in queryset:
            AlteredFetchDeckDataService(deck).handle()
        self.message_user(
            request,
            f"Updated {queryset.count()} deck(s)",
            messages.SUCCESS,
        )
