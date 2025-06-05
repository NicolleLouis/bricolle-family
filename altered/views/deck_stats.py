from django.shortcuts import render

from altered.forms.deck_filter import DeckFilterForm
from altered.models import Deck
from altered.services.deck_game_stats import DeckGameStatsService


def deck_stats_view(request):
    form = DeckFilterForm(request.GET)
    faction = None
    if form.is_valid():
        faction = form.cleaned_data.get('faction') or None

    decks = Deck.objects.select_related('champion')
    if faction:
        decks = decks.filter(champion__faction=faction)

    stats = [DeckGameStatsService(deck).result for deck in decks]
    stats.sort(key=lambda x: x.match_number, reverse=True)

    return render(request, 'altered/deck_stats.html', {'stats': stats, 'form': form})
