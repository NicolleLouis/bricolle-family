import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from slay_the_spire2.models import Character, Relic, RunFile, RunSummary
from slay_the_spire2.services.relic_stats import RelicStatsService


@pytest.mark.django_db
class TestRelicStatsService:
    def test_get_win_by_relic_number_points_filters_by_character(self):
        ironclad = Character.objects.create(name="IRONCLAD")
        silent = Character.objects.create(name="SILENT")
        relic_a = Relic.objects.create(name="RELIC A")
        relic_b = Relic.objects.create(name="RELIC B")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "service-chart-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917601, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "service-chart-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917602, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummary.objects.filter(id=run_file_1.summary.id).update(character=ironclad, win=True)
        RunSummary.objects.filter(id=run_file_2.summary.id).update(character=silent, win=False)
        run_file_1.summary.relics.set([relic_a])
        run_file_2.summary.relics.set([relic_a, relic_b])

        unfiltered_points = RelicStatsService().get_win_by_relic_number_points(character_id=None)
        filtered_points = RelicStatsService().get_win_by_relic_number_points(character_id=ironclad.id)

        assert unfiltered_points == [
            {"total_relic": 1, "win_ratio": 100.0},
            {"total_relic": 2, "win_ratio": 0.0},
        ]
        assert filtered_points == [{"total_relic": 1, "win_ratio": 100.0}]
