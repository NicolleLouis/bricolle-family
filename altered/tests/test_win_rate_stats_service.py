from django.test import TestCase

from altered.constants.win_rate_scope import WinRateScope
from altered.models import Champion, Deck, Game
from altered.services.win_rate_stats import WinRateStatsService


class WinRateStatsServiceTests(TestCase):
    def setUp(self):
        self.alpha = Champion.objects.create(name="Alpha", faction="AXIOM")
        self.beta = Champion.objects.create(name="Beta", faction="BRAVOS")
        self.gamma = Champion.objects.create(name="Gamma", faction="LYRA")
        self.delta = Champion.objects.create(name="Delta", faction="MUNA")

        self.deck_alpha = Deck.objects.create(name="Deck Alpha", champion=self.alpha, altered_id="deck-alpha")
        self.deck_beta = Deck.objects.create(name="Deck Beta", champion=self.beta, altered_id="deck-beta")

        Game.objects.create(deck=self.deck_alpha, opponent_champion=self.beta, is_win=True)
        Game.objects.create(deck=self.deck_alpha, opponent_champion=self.beta, is_win=False)
        Game.objects.create(deck=self.deck_alpha, opponent_champion=self.gamma, is_win=True)
        Game.objects.create(deck=self.deck_beta, opponent_champion=self.alpha, is_win=False)

    def test_default_scope_includes_all_champions(self):
        service = WinRateStatsService()

        alpha_stat = next(stat for stat in service.result if stat.champion == self.alpha)
        beta_stat = next(stat for stat in service.result if stat.champion == self.beta)
        gamma_stat = next(stat for stat in service.result if stat.champion == self.gamma)
        delta_stat = next(stat for stat in service.result if stat.champion == self.delta)

        self.assertEqual(alpha_stat.match_number, 1)
        self.assertEqual(alpha_stat.win_number, 0)
        self.assertIsNone(alpha_stat.win_ratio)

        self.assertEqual(beta_stat.match_number, 2)
        self.assertEqual(beta_stat.win_number, 1)
        self.assertEqual(beta_stat.win_ratio, 50.0)

        self.assertEqual(gamma_stat.match_number, 1)
        self.assertEqual(gamma_stat.win_number, 1)
        self.assertEqual(gamma_stat.win_ratio, 100.0)

        self.assertEqual(delta_stat.match_number, 0)
        self.assertEqual(delta_stat.win_number, 0)
        self.assertIsNone(delta_stat.win_ratio)

    def test_ratio_colors_follow_gradient(self):
        service = WinRateStatsService()

        alpha_stat = next(stat for stat in service.result if stat.champion == self.alpha)
        beta_stat = next(stat for stat in service.result if stat.champion == self.beta)
        gamma_stat = next(stat for stat in service.result if stat.champion == self.gamma)

        self.assertEqual(alpha_stat.ratio_color, "#dc3545")
        self.assertEqual(alpha_stat.ratio_text_color, "#ffffff")

        self.assertEqual(beta_stat.ratio_color, "#fd7e14")
        self.assertEqual(beta_stat.ratio_text_color, "#212529")

        self.assertEqual(gamma_stat.ratio_color, "#198754")
        self.assertEqual(gamma_stat.ratio_text_color, "#ffffff")

    def test_achievement_colors(self):
        service = WinRateStatsService()

        alpha_stat = next(stat for stat in service.result if stat.champion == self.alpha)
        beta_stat = next(stat for stat in service.result if stat.champion == self.beta)
        delta_stat = next(stat for stat in service.result if stat.champion == self.delta)

        self.assertEqual(alpha_stat.achievement_color, "#dc3545")
        self.assertEqual(beta_stat.achievement_color, "#198754")
        self.assertEqual(delta_stat.achievement_color, "#adb5bd")

    def test_scope_filter_by_faction(self):
        service = WinRateStatsService(scope=WinRateScope.FACTION, faction="AXIOM")

        alpha_stat = next(stat for stat in service.result if stat.champion == self.alpha)
        beta_stat = next(stat for stat in service.result if stat.champion == self.beta)

        self.assertEqual(alpha_stat.match_number, 0)
        self.assertEqual(alpha_stat.win_number, 0)
        self.assertIsNone(alpha_stat.win_ratio)

        self.assertEqual(beta_stat.match_number, 2)
        self.assertEqual(beta_stat.win_number, 1)

    def test_scope_filter_by_champion(self):
        service = WinRateStatsService(scope=WinRateScope.CHAMPION, champion=self.beta)

        alpha_stat = next(stat for stat in service.result if stat.champion == self.alpha)
        beta_stat = next(stat for stat in service.result if stat.champion == self.beta)

        self.assertEqual(alpha_stat.match_number, 1)
        self.assertEqual(alpha_stat.win_number, 0)
        self.assertIsNone(beta_stat.win_ratio)

    def test_scope_filter_by_deck(self):
        service = WinRateStatsService(scope=WinRateScope.DECK, deck=self.deck_beta)

        alpha_stat = next(stat for stat in service.result if stat.champion == self.alpha)
        beta_stat = next(stat for stat in service.result if stat.champion == self.beta)

        self.assertEqual(alpha_stat.match_number, 1)
        self.assertEqual(alpha_stat.win_number, 0)
        self.assertEqual(beta_stat.match_number, 0)
