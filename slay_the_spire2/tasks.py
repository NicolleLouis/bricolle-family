from celery import shared_task

from slay_the_spire2.services.reparse_run_files import ReparseRunFilesService


@shared_task
def reparse_all_run_files() -> dict:
    return ReparseRunFilesService().reparse_all()
