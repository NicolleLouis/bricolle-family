from celery import shared_task

from corwave.services.csv_enrichment_job_service import CorwaveCsvEnrichmentJobService


@shared_task
def run_corwave_enrichment_job(job_id: int) -> None:
    job_service = CorwaveCsvEnrichmentJobService()
    job_service.process_job(job_id=job_id)
