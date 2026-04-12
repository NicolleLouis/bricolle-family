import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from slay_the_spire2.models import Character, Encounter, RunEncounter, RunFile, RunSummary


@pytest.mark.django_db
class TestBossView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="boss-admin-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_boss_view_renders(self, authenticated_client):
        response = authenticated_client.get(reverse("slay_the_spire2:boss"))

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Boss" in page_content
        assert "Dangerousness" in page_content

    def test_boss_view_dangerousness_filters_by_character_and_act(self, authenticated_client):
        ironclad = Character.objects.create(name="IRONCLAD")
        silent = Character.objects.create(name="SILENT")
        time_eater = Encounter.objects.create(type=Encounter.Type.BOSS, name="Time Eater")
        awakened_one = Encounter.objects.create(type=Encounter.Type.BOSS, name="Awakened One")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "boss-view-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917901, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "boss-view-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917902, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_3 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "boss-view-3.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917903, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummary.objects.filter(id=run_file_1.summary.id).update(character=ironclad)
        RunSummary.objects.filter(id=run_file_2.summary.id).update(character=ironclad)
        RunSummary.objects.filter(id=run_file_3.summary.id).update(character=silent)

        RunEncounter.objects.create(
            run_summary=run_file_1.summary,
            encounter=time_eater,
            act=2,
            floor=1,
            damage_taken=30,
        )
        RunEncounter.objects.create(
            run_summary=run_file_2.summary,
            encounter=time_eater,
            act=2,
            floor=2,
            damage_taken=10,
        )
        RunEncounter.objects.create(
            run_summary=run_file_3.summary,
            encounter=awakened_one,
            act=2,
            floor=1,
            damage_taken=99,
        )

        response = authenticated_client.get(
            reverse("slay_the_spire2:boss"),
            {"character": str(ironclad.id), "act": "2"},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Average Damage Taken" in page_content
        assert "Time Eater" in page_content
        assert "20.0" in page_content
        assert "Awakened One" not in page_content
