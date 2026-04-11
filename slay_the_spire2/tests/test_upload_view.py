import io
import zipfile

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from slay_the_spire2.models import Encounter, RunFile, RunSummary


@pytest.mark.django_db
class TestUploadView:
    def _build_zip_upload_file(self, file_name_to_content: dict[str, bytes]) -> SimpleUploadedFile:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_name, file_content in file_name_to_content.items():
                archive.writestr(file_name, file_content)
        return SimpleUploadedFile(
            "runs.zip",
            buffer.getvalue(),
            content_type="application/zip",
        )

    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="upload-admin-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_upload_get_returns_page(self, authenticated_client):
        response = authenticated_client.get(reverse("slay_the_spire2:upload"))

        assert response.status_code == 200
        assert b"<h1 class=\"h3 mb-3\">Upload</h1>" in response.content

    def test_upload_post_creates_run_file_and_summary(self, authenticated_client):
        response = authenticated_client.post(
            reverse("slay_the_spire2:upload"),
            data={
                "run_file": SimpleUploadedFile(
                    "view-upload.run",
                    b'{"win": false, "was_abandoned": true, "start_time": 1772916800, "ascension": 2, "killed_by_encounter": "NONE.NONE", "killed_by_event": "EVENT.ROOM_TEST"}',
                    content_type="application/json",
                )
            },
            follow=True,
        )

        assert response.status_code == 200
        assert RunFile.objects.count() == 1
        assert RunSummary.objects.count() == 1
        assert RunFile.objects.first().summary.killed_by.name == "Room Test"
        assert RunFile.objects.first().summary.killed_by.type == Encounter.Type.ROOM
        assert b"Import termine" in response.content

    def test_upload_post_shows_error_for_invalid_file(self, authenticated_client):
        response = authenticated_client.post(
            reverse("slay_the_spire2:upload"),
            data={
                "run_file": SimpleUploadedFile(
                    "invalid-upload.run",
                    b'{"win": true',
                    content_type="application/json",
                )
            },
            follow=True,
        )

        assert response.status_code == 200
        assert RunFile.objects.count() == 0
        assert RunSummary.objects.count() == 0
        assert b"JSON valide" in response.content

    def test_upload_post_shows_error_when_start_time_already_exists(self, authenticated_client):
        authenticated_client.post(
            reverse("slay_the_spire2:upload"),
            data={
                "run_file": SimpleUploadedFile(
                    "first-upload.run",
                    b'{"win": true, "was_abandoned": false, "start_time": 1772916900, "ascension": 0, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                    content_type="application/json",
                )
            },
            follow=True,
        )

        response = authenticated_client.post(
            reverse("slay_the_spire2:upload"),
            data={
                "run_file": SimpleUploadedFile(
                    "duplicate-upload.run",
                    b'{"win": false, "was_abandoned": false, "start_time": 1772916900, "ascension": 3, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                    content_type="application/json",
                )
            },
            follow=True,
        )

        assert response.status_code == 200
        assert RunFile.objects.count() == 1
        assert RunSummary.objects.count() == 1
        assert b"existe deja en base" in response.content

    def test_upload_post_zip_imports_each_file(self, authenticated_client):
        zip_file = self._build_zip_upload_file(
            {
                "first.run": b'{"win": true, "was_abandoned": false, "start_time": 1772917000, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                "second.run": b'{"win": false, "was_abandoned": true, "start_time": 1772917001, "ascension": 2, "killed_by_encounter": "ENCOUNTER.KNIGHTS_ELITE", "killed_by_event": "NONE.NONE"}',
            }
        )

        response = authenticated_client.post(
            reverse("slay_the_spire2:upload"),
            data={"run_file": zip_file},
            follow=True,
        )

        assert response.status_code == 200
        assert RunFile.objects.count() == 2
        assert RunSummary.objects.count() == 2
        assert b"Import zip termine: 2/2 fichier(s) importe(s)." in response.content

    def test_upload_post_zip_continues_when_one_file_fails(self, authenticated_client):
        zip_file = self._build_zip_upload_file(
            {
                "first.run": b'{"win": true, "was_abandoned": false, "start_time": 1772917010, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                "duplicate.run": b'{"win": false, "was_abandoned": false, "start_time": 1772917010, "ascension": 3, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                "third.run": b'{"win": true, "was_abandoned": false, "start_time": 1772917012, "ascension": 0, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
            }
        )

        response = authenticated_client.post(
            reverse("slay_the_spire2:upload"),
            data={"run_file": zip_file},
            follow=True,
        )

        assert response.status_code == 200
        assert RunFile.objects.count() == 2
        assert RunSummary.objects.count() == 2
        assert b"Import zip termine: 2/3 fichier(s) importe(s)." in response.content
        assert b"duplicate.run: Une run avec start_time=1772917010 existe deja en base." in response.content
