from django.contrib import messages
from django.shortcuts import redirect, render

from slay_the_spire2.models.reparse_run_job import ReparseRunJob
from slay_the_spire2.tasks import reparse_all_run_files


def settings(request):
    if request.method == "POST":
        reparse_run_job = ReparseRunJob.objects.create(status=ReparseRunJob.Status.QUEUED)
        reparse_all_run_files.delay(reparse_run_job_id=reparse_run_job.id)
        messages.success(request, "Le reparse de tous les fichiers run a ete lance en asynchrone.")
        return redirect("slay_the_spire2:settings")

    last_reparse_job = ReparseRunJob.objects.order_by("-started_at").first()
    return render(
        request,
        "slay_the_spire2/settings.html",
        {"last_reparse_job": last_reparse_job},
    )
