from altered.models import Deck, Game
from altered.value_objects.deck_game_stats import DeckGameStats


class DeckGameStatsService:
    def __init__(self, deck: Deck):
        self.deck = deck
        self.result = DeckGameStats(deck=deck)
        self.games = Game.objects.filter(deck=deck)
        self.compute()

    def compute(self):
        self.result.match_number = self.games.count()
        self.result.win_number = self.games.filter(is_win=True).count()
        if self.result.match_number:
            ratio = self.result.win_number / self.result.match_number * 100
            self.result.win_ratio = round(ratio, 2)
        else:
            self.result.win_ratio = 0.0
