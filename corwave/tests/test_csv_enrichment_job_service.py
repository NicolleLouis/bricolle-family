from pathlib import Path

import pytest

from corwave.models import CorwaveEnrichmentJob
from corwave.services.csv_enrichment_job_service import (
    CorwaveCsvEnrichmentJobService,
    CorwaveCsvEnrichmentJobServiceError,
)
from corwave.services.csv_enrichment_service import (
    CorwaveCsvEnrichmentServiceError,
    CsvEnrichmentResult,
)


class FakeSuccessfulCsvEnrichmentService:
    def enrich_csv(
        self,
        *,
        csv_file_name: str,
        csv_file_content: bytes,
        progress_callback=None,
    ) -> CsvEnrichmentResult:
        if progress_callback is not None:
            progress_callback(1, 1)
        return CsvEnrichmentResult(filename="input_enriched.csv", content="Title,Abstract,article_type\nA,a,Review\n")


class FakeFailingCsvEnrichmentService:
    def enrich_csv(
        self,
        *,
        csv_file_name: str,
        csv_file_content: bytes,
        progress_callback=None,
    ) -> CsvEnrichmentResult:
        raise CorwaveCsvEnrichmentServiceError("upstream failed")


@pytest.mark.django_db
class TestCorwaveCsvEnrichmentJobService:
    def test_create_job_persists_input_file_and_row_count(self, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        service = CorwaveCsvEnrichmentJobService()

        job = service.create_job(
            csv_file_name="pubmed.csv",
            csv_file_content=b"Title,Abstract\nA,a\nB,b\n",
        )

        assert job.status == CorwaveEnrichmentJob.Status.PENDING
        assert job.total_rows == 2
        assert job.processed_rows == 0
        assert job.input_file_name == "pubmed.csv"
        assert Path(job.input_file.path).exists()

    def test_create_job_raises_error_when_header_is_missing(self):
        service = CorwaveCsvEnrichmentJobService()

        with pytest.raises(CorwaveCsvEnrichmentJobServiceError, match="header row"):
            service.create_job(csv_file_name="input.csv", csv_file_content=b"")

    def test_process_job_marks_done_and_saves_output_file(self, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        service = CorwaveCsvEnrichmentJobService(
            csv_enrichment_service=FakeSuccessfulCsvEnrichmentService()
        )
        job = service.create_job(
            csv_file_name="pubmed.csv",
            csv_file_content=b"Title,Abstract\nA,a\n",
        )

        service.process_job(job_id=job.id)

        job.refresh_from_db()
        assert job.status == CorwaveEnrichmentJob.Status.DONE
        assert job.output_file
        assert "input_enriched.csv" in job.output_file.name
        assert job.processed_rows == job.total_rows

    def test_process_job_marks_failed_when_enrichment_fails(self, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        service = CorwaveCsvEnrichmentJobService(
            csv_enrichment_service=FakeFailingCsvEnrichmentService()
        )
        job = service.create_job(
            csv_file_name="pubmed.csv",
            csv_file_content=b"Title,Abstract\nA,a\n",
        )

        service.process_job(job_id=job.id)

        job.refresh_from_db()
        assert job.status == CorwaveEnrichmentJob.Status.FAILED
        assert "upstream failed" in job.error_message

    def test_process_job_updates_processed_rows_through_progress_callback(self, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        service = CorwaveCsvEnrichmentJobService(
            csv_enrichment_service=FakeSuccessfulCsvEnrichmentService()
        )
        job = service.create_job(
            csv_file_name="pubmed.csv",
            csv_file_content=b"Title,Abstract\nA,a\n",
        )

        service.process_job(job_id=job.id)

        job.refresh_from_db()
        assert job.processed_rows == 1
