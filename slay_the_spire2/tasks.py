import logging

from celery import shared_task
from django.utils import timezone

from slay_the_spire2.models.reparse_run_job import ReparseRunJob
from slay_the_spire2.services.reparse_run_files import ReparseRunFilesService

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def reparse_all_run_files(self, reparse_run_job_id: int | None = None) -> dict:
    if reparse_run_job_id is not None:
        ReparseRunJob.objects.filter(id=reparse_run_job_id).update(
            status=ReparseRunJob.Status.RUNNING,
            task_id=self.request.id or "",
            error_message="",
        )

    try:
        result = ReparseRunFilesService().reparse_all()
    except Exception as error:
        if reparse_run_job_id is not None:
            ReparseRunJob.objects.filter(id=reparse_run_job_id).update(
                status=ReparseRunJob.Status.FAILED,
                finished_at=timezone.now(),
                error_message=str(error),
            )
        logger.exception("Reparse global run files task failed.")
        raise

    if reparse_run_job_id is not None:
        ReparseRunJob.objects.filter(id=reparse_run_job_id).update(
            status=ReparseRunJob.Status.SUCCESS,
            reparsed_count=result.get("reparsed_count", 0),
            error_count=result.get("error_count", 0),
            finished_at=timezone.now(),
            error_message="",
        )
    return result
