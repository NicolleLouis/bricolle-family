import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from slay_the_spire2.models import Character, RunFile, RunSummary


@pytest.mark.django_db
class TestCharacterView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="character-admin-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_character_view_displays_aggregated_stats_sorted_by_win_number(self, authenticated_client):
        ironclad = Character.objects.create(name="IRONCLAD")
        silent = Character.objects.create(name="SILENT")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "character-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917101, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "character-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917102, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_3 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "character-3.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917103, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_4 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "character-4.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917104, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_5 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "character-5.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917105, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummary.objects.filter(id=run_file_1.summary.id).update(character=ironclad, win=True)
        RunSummary.objects.filter(id=run_file_2.summary.id).update(character=ironclad, win=True)
        RunSummary.objects.filter(id=run_file_3.summary.id).update(character=ironclad, win=False)
        RunSummary.objects.filter(id=run_file_4.summary.id).update(character=silent, win=True)
        RunSummary.objects.filter(id=run_file_5.summary.id).update(character=silent, win=False)

        response = authenticated_client.get(reverse("slay_the_spire2:character"))

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")

        assert "IRONCLAD" in page_content
        assert "SILENT" in page_content
        assert "66.67%" in page_content
        assert "50.0%" in page_content
        assert page_content.index("IRONCLAD") < page_content.index("SILENT")

    def test_character_view_supports_sort_query_params(self, authenticated_client):
        ironclad = Character.objects.create(name="IRONCLAD")
        silent = Character.objects.create(name="SILENT")

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "character-sort-1.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772917201, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "character-sort-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917202, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummary.objects.filter(id=run_file_1.summary.id).update(character=silent, win=True)
        RunSummary.objects.filter(id=run_file_2.summary.id).update(character=ironclad, win=False)

        response = authenticated_client.get(
            reverse("slay_the_spire2:character"),
            {"sort": "character_name", "direction": "asc"},
        )

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert page_content.index("IRONCLAD") < page_content.index("SILENT")
