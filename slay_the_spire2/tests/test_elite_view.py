import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from slay_the_spire2.models import Character, Encounter, RunEncounter, RunFile, RunSummary


@pytest.mark.django_db
class TestEliteView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="elite-admin-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_elite_view_renders(self, authenticated_client):
        response = authenticated_client.get(reverse("slay_the_spire2:elite"))

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Elite" in page_content
        assert "Win Rate" in page_content

    def test_elite_view_win_rate_tab_renders_four_charts(self, authenticated_client):
        elite_encounter = Encounter.objects.create(type=Encounter.Type.ELITE, name="Lagavulin")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "elite-view-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917801, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "elite-view-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917802, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunEncounter.objects.create(
            run_summary=run_file_1.summary,
            encounter=elite_encounter,
            act=0,
            floor=1,
            damage_taken=10,
        )
        RunEncounter.objects.create(
            run_summary=run_file_1.summary,
            encounter=elite_encounter,
            act=1,
            floor=2,
            damage_taken=8,
        )
        RunEncounter.objects.create(
            run_summary=run_file_1.summary,
            encounter=elite_encounter,
            act=2,
            floor=3,
            damage_taken=5,
        )
        RunEncounter.objects.create(
            run_summary=run_file_2.summary,
            encounter=elite_encounter,
            act=0,
            floor=1,
            damage_taken=12,
        )

        response = authenticated_client.get(
            reverse("slay_the_spire2:elite"),
            {"tab": "win_rate"},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Win Ratio and Run Count by Elite Encountered Count" in page_content
        assert "Act 1 - Win Ratio and Run Count by Elite Encountered Count" in page_content
        assert "Act 2 - Win Ratio and Run Count by Elite Encountered Count" in page_content
        assert "Act 3 - Win Ratio and Run Count by Elite Encountered Count" in page_content

    def test_elite_view_dangerousness_tab_renders_table_and_filters(self, authenticated_client):
        ironclad = Character.objects.create(name="IRONCLAD")
        silent = Character.objects.create(name="SILENT")
        lagavulin = Encounter.objects.create(type=Encounter.Type.ELITE, name="Lagavulin")
        sentries = Encounter.objects.create(type=Encounter.Type.ELITE, name="Sentries")
        time_eater = Encounter.objects.create(type=Encounter.Type.BOSS, name="Time Eater")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "elite-danger-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917803, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "elite-danger-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917804, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_3 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "elite-danger-3.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917805, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummary.objects.filter(id=run_file_1.summary.id).update(character=ironclad)
        RunSummary.objects.filter(id=run_file_2.summary.id).update(character=ironclad)
        RunSummary.objects.filter(id=run_file_3.summary.id).update(character=silent)

        RunEncounter.objects.create(
            run_summary=run_file_1.summary,
            encounter=lagavulin,
            act=1,
            floor=1,
            damage_taken=10,
        )
        RunEncounter.objects.create(
            run_summary=run_file_1.summary,
            encounter=time_eater,
            act=1,
            floor=9,
            damage_taken=77,
        )
        RunEncounter.objects.create(
            run_summary=run_file_2.summary,
            encounter=lagavulin,
            act=1,
            floor=2,
            damage_taken=20,
        )
        RunEncounter.objects.create(
            run_summary=run_file_3.summary,
            encounter=sentries,
            act=1,
            floor=1,
            damage_taken=99,
        )

        response = authenticated_client.get(
            reverse("slay_the_spire2:elite"),
            {"tab": "dangerousness", "character": str(ironclad.id), "act": "1"},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Average Damage Taken" in page_content
        assert "Lagavulin" in page_content
        assert "15.0" in page_content
        assert "Sentries" not in page_content
        assert "Time Eater" not in page_content
