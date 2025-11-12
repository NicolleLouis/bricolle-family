from unittest.mock import MagicMock, patch

from django.test import TestCase

from altered.models import Champion
from altered.services.opponent_faction_chart import OpponentFactionChartService
from altered.value_objects.champion_game_stats import ChampionGameStats


class OpponentFactionChartServiceTests(TestCase):
    def setUp(self):
        self.axiom = Champion.objects.create(name="Alpha", faction="AXIOM")
        self.axiom_two = Champion.objects.create(name="Omega", faction="AXIOM")
        self.bravos = Champion.objects.create(name="Bravo", faction="BRAVOS")

    @patch("altered.services.opponent_faction_chart.px")
    def test_render_builds_chart_with_faction_totals(self, mock_px):
        mock_fig = MagicMock()
        mock_fig.to_html.return_value = "<div>chart</div>"
        mock_px.pie.return_value = mock_fig

        stats = [
            ChampionGameStats(champion=self.axiom, match_number=3),
            ChampionGameStats(champion=self.axiom_two, match_number=2),
            ChampionGameStats(champion=self.bravos, match_number=1),
        ]

        html = OpponentFactionChartService(stats).render()

        self.assertEqual(html, "<div>chart</div>")
        mock_px.pie.assert_called_once()
        _, kwargs = mock_px.pie.call_args
        self.assertEqual(kwargs["names"], ["Axiom", "Bravos"])
        self.assertEqual(kwargs["values"], [5, 1])
        self.assertEqual(kwargs["color"], ["Axiom", "Bravos"])
        self.assertEqual(kwargs["color_discrete_map"]["Axiom"], "#B34F2B")

    @patch("altered.services.opponent_faction_chart.px")
    def test_render_returns_empty_string_when_no_matches(self, mock_px):
        stats = [
            ChampionGameStats(champion=self.axiom, match_number=0),
        ]

        html = OpponentFactionChartService(stats).render()

        self.assertEqual(html, "")
        mock_px.pie.assert_not_called()
