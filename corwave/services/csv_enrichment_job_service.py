from __future__ import annotations

import csv
import inspect
import io
from datetime import timedelta
from pathlib import Path

from django.core.files.base import ContentFile
from django.utils import timezone

from corwave.models import CorwaveEnrichmentJob
from corwave.services.csv_enrichment_service import (
    CorwaveCsvEnrichmentService,
    CorwaveCsvEnrichmentServiceError,
)


class CorwaveCsvEnrichmentJobServiceError(RuntimeError):
    """Raised when a job cannot be created or processed."""


class CorwaveCsvEnrichmentJobService:
    _SECONDS_PER_ROW = 2

    def __init__(self, csv_enrichment_service: CorwaveCsvEnrichmentService | None = None) -> None:
        self._csv_enrichment_service = csv_enrichment_service or CorwaveCsvEnrichmentService()

    def create_job(self, *, csv_file_name: str, csv_file_content: bytes) -> CorwaveEnrichmentJob:
        total_rows = self._count_data_rows(csv_file_content=csv_file_content)
        cleaned_name = self._clean_file_name(csv_file_name)

        job = CorwaveEnrichmentJob(
            status=CorwaveEnrichmentJob.Status.PENDING,
            input_file_name=cleaned_name,
            total_rows=total_rows,
            processed_rows=0,
            error_message="",
        )
        job.input_file.save(cleaned_name, ContentFile(csv_file_content), save=False)
        job.save()
        return job

    def process_job(self, *, job_id: int) -> None:
        job = CorwaveEnrichmentJob.objects.get(id=job_id)
        if job.status == CorwaveEnrichmentJob.Status.DONE:
            return

        job.status = CorwaveEnrichmentJob.Status.PROCESSING
        job.started_at = timezone.now()
        job.error_message = ""
        job.save(update_fields=["status", "started_at", "error_message"])

        try:
            input_bytes = self._read_input_bytes(job=job)
            enrichment_result = self._run_enrichment(
                job=job,
                csv_file_content=input_bytes,
            )
            output_file_name = self._build_output_file_name(
                job_id=job.id,
                file_name=enrichment_result.filename,
            )
            job.output_file.save(
                output_file_name,
                ContentFile(enrichment_result.content.encode("utf-8")),
                save=False,
            )
            job.status = CorwaveEnrichmentJob.Status.DONE
            job.processed_rows = job.total_rows
            job.finished_at = timezone.now()
            job.save(update_fields=["output_file", "status", "processed_rows", "finished_at"])
        except CorwaveCsvEnrichmentServiceError as service_error:
            job.status = CorwaveEnrichmentJob.Status.FAILED
            job.error_message = str(service_error)
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error_message", "finished_at"])

    def build_eta_seconds(self, *, total_rows: int) -> int:
        return total_rows * self._SECONDS_PER_ROW

    def build_estimated_finish_time(self, *, eta_seconds: int):
        return timezone.now() + timedelta(seconds=eta_seconds)

    @staticmethod
    def _count_data_rows(*, csv_file_content: bytes) -> int:
        try:
            decoded_content = csv_file_content.decode("utf-8-sig")
        except UnicodeDecodeError as decode_error:
            raise CorwaveCsvEnrichmentJobServiceError("CSV encoding must be UTF-8.") from decode_error

        reader = csv.DictReader(io.StringIO(decoded_content))
        if not reader.fieldnames:
            raise CorwaveCsvEnrichmentJobServiceError("CSV must contain a header row.")

        return sum(1 for _ in reader)

    @staticmethod
    def _clean_file_name(file_name: str) -> str:
        candidate_name = (file_name or "").strip() or "input.csv"
        return Path(candidate_name).name

    @staticmethod
    def _read_input_bytes(*, job: CorwaveEnrichmentJob) -> bytes:
        with job.input_file.open("rb") as input_stream:
            return input_stream.read()

    @staticmethod
    def _build_output_file_name(*, job_id: int, file_name: str) -> str:
        return f"job_{job_id}_{Path(file_name).name}"

    def _run_enrichment(
        self,
        *,
        job: CorwaveEnrichmentJob,
        csv_file_content: bytes,
    ):
        def on_progress(processed_rows: int, total_rows: int) -> None:
            CorwaveEnrichmentJob.objects.filter(id=job.id).update(
                processed_rows=processed_rows,
                total_rows=total_rows,
            )

        enrich_csv_signature = inspect.signature(self._csv_enrichment_service.enrich_csv)
        if "progress_callback" in enrich_csv_signature.parameters:
            return self._csv_enrichment_service.enrich_csv(
                csv_file_name=job.input_file_name,
                csv_file_content=csv_file_content,
                progress_callback=on_progress,
            )
        return self._csv_enrichment_service.enrich_csv(
            csv_file_name=job.input_file_name,
            csv_file_content=csv_file_content,
        )
