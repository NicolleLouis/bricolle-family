from django.shortcuts import render

from altered.forms.deck_filter import DeckFilterForm
from altered.models import Deck
from altered.services.deck_game_stats import DeckGameStatsService


def deck_stats_view(request):
    form = DeckFilterForm(request.GET or {"only_active": True})
    faction = None
    only_active = True
    if form.is_valid():
        faction = form.cleaned_data.get('faction') or None
        only_active = form.cleaned_data.get('only_active')

    decks = Deck.objects.select_related('champion')
    if only_active:
        decks = decks.filter(is_active=True)
    if faction:
        decks = decks.filter(champion__faction=faction)

    stats = [DeckGameStatsService(deck).result for deck in decks]
    stats.sort(key=lambda x: x.match_number, reverse=True)

    return render(request, 'altered/deck_stats.html', {'stats': stats, 'form': form})
