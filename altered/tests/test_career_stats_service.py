from django.test import TestCase

from altered.models import Champion, Deck, Game
from altered.services.career_stats import CareerStatsService


class CareerStatsServiceTests(TestCase):
    def setUp(self):
        self.champ1 = Champion.objects.create(name="Alpha", faction="AXIOM")
        self.champ2 = Champion.objects.create(name="Beta", faction="BRAVOS")
        self.champ3 = Champion.objects.create(name="Gamma", faction="LYRA")
        self.deck = Deck.objects.create(name="Deck1", champion=self.champ1, altered_id="1")
        Game.objects.create(deck=self.deck, opponent_champion=self.champ2, is_win=True)
        Game.objects.create(deck=self.deck, opponent_champion=self.champ2, is_win=False)
        Game.objects.create(deck=self.deck, opponent_champion=self.champ2, is_win=True)

    def test_compute_win_numbers(self):
        service = CareerStatsService()
        alpha_stat = next(s for s in service.result if s.champion == self.champ1)
        self.assertEqual(alpha_stat.win_number, 2)
        beta_stat = next(s for s in service.result if s.champion == self.champ2)
        self.assertEqual(beta_stat.win_number, 0)

    def test_missing_only_filter(self):
        service = CareerStatsService(missing_only=True)
        champs = [stat.champion for stat in service.result]
        self.assertIn(self.champ2, champs)
        self.assertIn(self.champ3, champs)
        self.assertNotIn(self.champ1, champs)
