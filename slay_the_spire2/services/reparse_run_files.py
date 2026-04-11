import logging
import os

from django.db import transaction

from slay_the_spire2.models.run_file import RunFile
from slay_the_spire2.services.run_file_parser import RunFileParserService
from slay_the_spire2.services.run_summary_builder import RunSummaryBuilderService

logger = logging.getLogger(__name__)


class ReparseRunFilesService:
    def __init__(self):
        self._run_file_parser_service = RunFileParserService()
        self._run_summary_builder_service = RunSummaryBuilderService()

    def reparse_all(self) -> dict:
        reparsed_count = 0
        error_count = 0

        for run_file in RunFile.objects.iterator():
            try:
                self.reparse_one(run_file)
                reparsed_count += 1
            except ValueError as error:
                error_count += 1
                logger.exception("Unable to reparse run file id=%s: %s", run_file.id, error)

        return {"reparsed_count": reparsed_count, "error_count": error_count}

    def reparse_one(self, run_file: RunFile) -> None:
        parsed_payload = self._run_file_parser_service.parse_uploaded_file(run_file.file)
        run_file.original_file_name = os.path.basename(run_file.file.name)
        run_file.parsed_payload = parsed_payload

        with transaction.atomic():
            RunFile.objects.filter(id=run_file.id).update(
                original_file_name=run_file.original_file_name,
                parsed_payload=run_file.parsed_payload,
            )
            self._run_summary_builder_service.upsert_from_run_file(run_file)
