import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from slay_the_spire2.models import Card, Character, RunFile, RunSummary, RunSummaryCard
from slay_the_spire2.services.card_stats import CardStatsService


@pytest.mark.django_db
class TestCardStatsService:
    def test_get_win_by_card_number_points_filters_by_character(self):
        ironclad = Character.objects.create(name="IRONCLAD")
        silent = Character.objects.create(name="SILENT")
        card_a = Card.objects.create(name="CARD A")
        card_b = Card.objects.create(name="CARD B")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "service-card-chart-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772918601, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "service-card-chart-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772918602, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummary.objects.filter(id=run_file_1.summary.id).update(character=ironclad, win=True)
        RunSummary.objects.filter(id=run_file_2.summary.id).update(character=silent, win=False)
        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=card_a, quantity=2)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=card_a, quantity=1)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=card_b, quantity=1)

        unfiltered_points = CardStatsService().get_win_by_card_number_points(character_id=None)
        filtered_points = CardStatsService().get_win_by_card_number_points(character_id=ironclad.id)

        assert unfiltered_points == [
            {"total_card": 2, "win_ratio": 50.0},
        ]
        assert filtered_points == [{"total_card": 2, "win_ratio": 100.0}]

    def test_get_basic_card_impact_points(self):
        strike = Card.objects.create(name="Strike")
        defend = Card.objects.create(name="Defend")
        bodyguard = Card.objects.create(name="Bodyguard")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "service-basic-card-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772918701, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "service-basic-card-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772918702, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=strike, quantity=2)
        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=defend, quantity=1)
        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=bodyguard, quantity=3)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=strike, quantity=1)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=defend, quantity=2)

        basic_chart = CardStatsService().get_win_by_basic_card_count_chart()
        strike_chart = CardStatsService().get_win_by_strike_count_chart()
        defend_chart = CardStatsService().get_win_by_defend_count_chart()

        assert "Win Ratio and Run Count by Strike + Defend Count" in basic_chart
        assert "Run Count" in basic_chart
        assert "Win Ratio" in basic_chart
        assert "Win Ratio and Run Count by Strike Count" in strike_chart
        assert "Run Count" in strike_chart
        assert "Win Ratio" in strike_chart
        assert "Win Ratio and Run Count by Defend Count" in defend_chart
        assert "Run Count" in defend_chart
        assert "Win Ratio" in defend_chart
