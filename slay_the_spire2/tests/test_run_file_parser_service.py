import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from slay_the_spire2.services.run_file_parser import RunFileParserService


class TestRunFileParserService:
    def test_parse_uploaded_file_returns_json_payload(self):
        uploaded_file = SimpleUploadedFile(
            "example.run",
            b'{"character_chosen": "IRONCLAD", "score": 123}',
            content_type="application/json",
        )

        payload = RunFileParserService().parse_uploaded_file(uploaded_file)

        assert payload == {"character_chosen": "IRONCLAD", "score": 123}

    def test_parse_uploaded_file_raises_error_when_json_is_invalid(self):
        uploaded_file = SimpleUploadedFile(
            "invalid.run",
            b'{"character_chosen": "IRONCLAD"',
            content_type="application/json",
        )

        with pytest.raises(ValueError, match="JSON valide"):
            RunFileParserService().parse_uploaded_file(uploaded_file)

    def test_parse_uploaded_file_raises_error_when_json_is_not_an_object(self):
        uploaded_file = SimpleUploadedFile(
            "list.run",
            b'["IRONCLAD", "SILENT"]',
            content_type="application/json",
        )

        with pytest.raises(ValueError, match="objet JSON"):
            RunFileParserService().parse_uploaded_file(uploaded_file)
