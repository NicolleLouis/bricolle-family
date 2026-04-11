import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from slay_the_spire2.models import Encounter, RunFile, RunSummary


@pytest.mark.django_db
class TestDeathTypeView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="death-type-admin-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_death_type_view_displays_encounters_sorted_by_death_count_desc(self, authenticated_client):
        knights = Encounter.objects.create(name="Knights", type=Encounter.Type.ELITE)
        boss = Encounter.objects.create(name="Big Boss", type=Encounter.Type.BOSS)
        zero_count = Encounter.objects.create(name="No Death", type=Encounter.Type.MONSTER)

        run_file_1 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "death-1.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917501, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_2 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "death-2.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917502, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )
        run_file_3 = RunFile.objects.create(
            file=SimpleUploadedFile(
                "death-3.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772917503, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        RunSummary.objects.filter(id=run_file_1.summary.id).update(killed_by=knights)
        RunSummary.objects.filter(id=run_file_2.summary.id).update(killed_by=knights)
        RunSummary.objects.filter(id=run_file_3.summary.id).update(killed_by=boss)

        response = authenticated_client.get(reverse("slay_the_spire2:death_type"))

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Knights" in page_content
        assert "Big Boss" in page_content
        assert "No Death" not in page_content
        assert page_content.index("Knights") < page_content.index("Big Boss")
        assert "2" in page_content
        assert "1" in page_content
