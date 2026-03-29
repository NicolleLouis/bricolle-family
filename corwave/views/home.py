from pathlib import Path

from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from corwave.models import CorwaveEnrichmentJob
from corwave.services.csv_enrichment_job_service import (
    CorwaveCsvEnrichmentJobService,
    CorwaveCsvEnrichmentJobServiceError,
)
from corwave.tasks import run_corwave_enrichment_job


def home(request):
    if request.method == "POST":
        return _handle_job_creation(request)

    return render(request, "corwave/home.html")


def job_status(request, job_id: int):
    job = get_object_or_404(CorwaveEnrichmentJob, id=job_id)

    response_payload = {
        "job_id": job.id,
        "status": job.status,
        "total_rows": job.total_rows,
        "processed_rows": job.processed_rows,
    }

    if job.status == CorwaveEnrichmentJob.Status.DONE and job.output_file:
        response_payload["message"] = "Traitement terminé. Téléchargement disponible."
        response_payload["download_url"] = reverse("corwave:job_download", args=[job.id])
    elif job.status == CorwaveEnrichmentJob.Status.FAILED:
        response_payload["message"] = f"Traitement échoué: {job.error_message}"
    elif job.status == CorwaveEnrichmentJob.Status.PROCESSING:
        response_payload["message"] = (
            f"Traitement en cours ({job.processed_rows}/{job.total_rows} lignes)..."
        )
    else:
        response_payload["message"] = "Traitement en attente de démarrage..."

    return JsonResponse(response_payload)


def job_download(request, job_id: int):
    job = get_object_or_404(CorwaveEnrichmentJob, id=job_id)
    if job.status != CorwaveEnrichmentJob.Status.DONE or not job.output_file:
        return HttpResponse("Le fichier n'est pas encore disponible.", status=409)

    output_name = Path(job.output_file.name).name
    return FileResponse(job.output_file.open("rb"), as_attachment=True, filename=output_name)


def _handle_job_creation(request):
    uploaded_csv = request.FILES.get("csv_file")

    if not uploaded_csv:
        return render(
            request,
            "corwave/home.html",
            {"error_message": "Veuillez sélectionner un fichier CSV."},
        )

    job_service = CorwaveCsvEnrichmentJobService()
    try:
        job = job_service.create_job(
            csv_file_name=uploaded_csv.name,
            csv_file_content=uploaded_csv.read(),
        )
    except CorwaveCsvEnrichmentJobServiceError as service_error:
        return render(
            request,
            "corwave/home.html",
            {"error_message": str(service_error)},
        )

    eta_seconds = job_service.build_eta_seconds(total_rows=job.total_rows)
    estimated_finish_time = job_service.build_estimated_finish_time(eta_seconds=eta_seconds)
    eta_message = (
        f"Calcul fini dans {eta_seconds} secondes vers {estimated_finish_time.strftime('%H:%M')}."
    )

    run_corwave_enrichment_job.delay(job.id)

    return render(
        request,
        "corwave/home.html",
        {
            "job_id": job.id,
            "eta_message": eta_message,
            "status_url": reverse("corwave:job_status", args=[job.id]),
        },
    )
