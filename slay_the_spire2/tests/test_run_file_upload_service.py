import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from slay_the_spire2.models import RunFile, RunSummary
from slay_the_spire2.services.run_file_upload import RunFileUploadService


@pytest.mark.django_db
class TestRunFileUploadService:
    def test_upload_run_file_creates_run_file_and_summary(self):
        run_file = RunFileUploadService().upload_run_file(
            SimpleUploadedFile(
                "service-upload.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772916700, "ascension": 4, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE", "players": [{"character": "CHARACTER.DEFECT"}]}',
                content_type="application/json",
            )
        )

        assert run_file.original_file_name == "service-upload.run"
        assert run_file.summary.character.name == "DEFECT"
        assert run_file.summary.start_time == 1772916700
        assert run_file.summary.ascension == 4
        assert RunSummary.objects.count() == 1

    def test_upload_run_file_raises_error_when_start_time_already_exists(self):
        RunFile.objects.create(
            file=SimpleUploadedFile(
                "first.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772916711, "ascension": 1, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        with pytest.raises(ValidationError, match="existe deja en base"):
            RunFileUploadService().upload_run_file(
                SimpleUploadedFile(
                    "duplicate.run",
                    b'{"win": false, "was_abandoned": false, "start_time": 1772916711, "ascension": 2, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE"}',
                    content_type="application/json",
                )
            )

        assert RunFile.objects.count() == 1
        assert RunSummary.objects.count() == 1
