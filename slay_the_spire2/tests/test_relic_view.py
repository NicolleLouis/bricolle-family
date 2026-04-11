import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from slay_the_spire2.models import Character, Relic, RunFile, RunSummary


@pytest.mark.django_db
class TestRelicView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="relic-admin-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_relic_view_displays_stats_sorted_by_win_number_desc(self, authenticated_client):
        sparkling_rouge = Relic.objects.create(name="SPARKLING ROUGE")
        old_coin = Relic.objects.create(name="OLD COIN")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "relic-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917301, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "relic-2.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917302, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_3 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "relic-3.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917303, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        run_file_1.summary.relics.set([sparkling_rouge])
        run_file_2.summary.relics.set([sparkling_rouge])
        run_file_3.summary.relics.set([old_coin])

        response = authenticated_client.get(reverse("slay_the_spire2:relic"))

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "SPARKLING ROUGE" in page_content
        assert "OLD COIN" in page_content
        assert page_content.index("SPARKLING ROUGE") < page_content.index("OLD COIN")

    def test_relic_view_supports_sort_query_params(self, authenticated_client):
        aaa_relic = Relic.objects.create(name="AAA RELIC")
        zzz_relic = Relic.objects.create(name="ZZZ RELIC")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "relic-sort-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917311, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "relic-sort-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917312, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        run_file_1.summary.relics.set([zzz_relic])
        run_file_2.summary.relics.set([aaa_relic])

        response = authenticated_client.get(
            reverse("slay_the_spire2:relic"),
            {"sort": "relic_name", "direction": "asc"},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert page_content.index("AAA RELIC") < page_content.index("ZZZ RELIC")

    def test_relic_view_filters_by_selected_character(self, authenticated_client):
        ironclad = Character.objects.create(name="IRONCLAD")
        silent = Character.objects.create(name="SILENT")
        filtered_relic = Relic.objects.create(name="FILTERED RELIC")
        other_relic = Relic.objects.create(name="OTHER RELIC")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "relic-filter-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917401, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "relic-filter-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917402, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummary.objects.filter(id=run_file_1.summary.id).update(character=ironclad)
        RunSummary.objects.filter(id=run_file_2.summary.id).update(character=silent)
        run_file_1.summary.relics.set([filtered_relic])
        run_file_2.summary.relics.set([other_relic])

        response = authenticated_client.get(
            reverse("slay_the_spire2:relic"),
            {"character": str(ironclad.id)},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "FILTERED RELIC" in page_content
        assert "OTHER RELIC" not in page_content

    def test_relic_view_win_by_relic_number_tab_renders_chart(self, authenticated_client):
        relic_a = Relic.objects.create(name="RELIC A")
        relic_b = Relic.objects.create(name="RELIC B")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "relic-chart-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917411, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "relic-chart-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917412, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        run_file_1.summary.relics.set([relic_a])
        run_file_2.summary.relics.set([relic_a, relic_b])

        response = authenticated_client.get(
            reverse("slay_the_spire2:relic"),
            {"tab": "win_by_relic_number"},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Win Ratio by Total Relic Count" in page_content
