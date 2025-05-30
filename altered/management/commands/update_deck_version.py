from django.core.management.base import BaseCommand

from altered.models import Deck
from altered.services.altered_fetch_deck_data import AlteredFetchDeckDataService


class Command(BaseCommand):
    help = "Update all deck data from altered website"

    def handle(self, *args, **kwargs):
        decks = Deck.objects.all()
        for deck in decks:
            AlteredFetchDeckDataService(deck).handle()
