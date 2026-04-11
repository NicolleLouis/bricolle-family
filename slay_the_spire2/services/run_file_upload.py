from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from slay_the_spire2.models import RunFile, RunSummary
from slay_the_spire2.services.run_file_parser import RunFileParserService


class RunFileUploadService:
    def upload_run_file(self, uploaded_file: UploadedFile) -> RunFile:
        parsed_payload = RunFileParserService().parse_uploaded_file(uploaded_file)
        start_time = parsed_payload.get("start_time")

        if isinstance(start_time, int) and RunSummary.objects.filter(start_time=start_time).exists():
            raise ValidationError(
                {"file": f"Une run avec start_time={start_time} existe deja en base."}
            )

        return RunFile.objects.create(file=uploaded_file)
