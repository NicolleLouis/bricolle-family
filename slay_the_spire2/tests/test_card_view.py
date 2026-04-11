import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from slay_the_spire2.models import Card, Character, RunFile, RunSummary, RunSummaryCard


@pytest.mark.django_db
class TestCardView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="card-admin-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_card_view_displays_stats_sorted_by_win_number_desc(self, authenticated_client):
        bodyguard = Card.objects.create(name="Bodyguard")
        strike = Card.objects.create(name="Strike")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772918301, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-2.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772918302, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_3 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-3.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772918303, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=bodyguard, quantity=2)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=bodyguard, quantity=1)
        RunSummaryCard.objects.create(run_summary=run_file_3.summary, card=strike, quantity=1)

        response = authenticated_client.get(reverse("slay_the_spire2:card"))

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Bodyguard" in page_content
        assert "Strike" in page_content
        assert page_content.index("Bodyguard") < page_content.index("Strike")

    def test_card_view_supports_sort_query_params(self, authenticated_client):
        aaa_card = Card.objects.create(name="Aaa Card")
        zzz_card = Card.objects.create(name="Zzz Card")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-sort-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772918311, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-sort-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772918312, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=zzz_card, quantity=1)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=aaa_card, quantity=1)

        response = authenticated_client.get(
            reverse("slay_the_spire2:card"),
            {"sort": "card_name", "direction": "asc"},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert page_content.index("Aaa Card") < page_content.index("Zzz Card")

    def test_card_view_filters_by_selected_character(self, authenticated_client):
        ironclad = Character.objects.create(name="IRONCLAD")
        silent = Character.objects.create(name="SILENT")
        filtered_card = Card.objects.create(name="Filtered Card")
        other_card = Card.objects.create(name="Other Card")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-filter-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772918401, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-filter-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772918402, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummary.objects.filter(id=run_file_1.summary.id).update(character=ironclad)
        RunSummary.objects.filter(id=run_file_2.summary.id).update(character=silent)
        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=filtered_card, quantity=2)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=other_card, quantity=1)

        response = authenticated_client.get(
            reverse("slay_the_spire2:card"),
            {"character": str(ironclad.id)},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Filtered Card" in page_content
        assert "Other Card" not in page_content

    def test_card_view_win_by_card_number_tab_renders_chart(self, authenticated_client):
        card_a = Card.objects.create(name="Card A")
        card_b = Card.objects.create(name="Card B")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-chart-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772918411, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-chart-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772918412, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=card_a, quantity=1)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=card_a, quantity=1)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=card_b, quantity=1)

        response = authenticated_client.get(
            reverse("slay_the_spire2:card"),
            {"tab": "win_by_card_number"},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Win Ratio by Total Card Count" in page_content

    def test_card_view_basic_card_impact_tab_renders_three_charts(self, authenticated_client):
        strike = Card.objects.create(name="Strike")
        defend = Card.objects.create(name="Defend")
        bodyguard = Card.objects.create(name="Bodyguard")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-basic-impact-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772918421, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "card-basic-impact-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772918422, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=strike, quantity=2)
        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=defend, quantity=1)
        RunSummaryCard.objects.create(run_summary=run_file_1.summary, card=bodyguard, quantity=1)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=strike, quantity=1)
        RunSummaryCard.objects.create(run_summary=run_file_2.summary, card=defend, quantity=2)

        response = authenticated_client.get(
            reverse("slay_the_spire2:card"),
            {"tab": "basic_card_impact"},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Win Ratio and Run Count by Strike + Defend Count" in page_content
        assert "Win Ratio and Run Count by Strike Count" in page_content
        assert "Win Ratio and Run Count by Defend Count" in page_content
