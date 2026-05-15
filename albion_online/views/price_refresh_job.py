from django.http import JsonResponse

from albion_online.models import PriceRefreshJob


def price_refresh_job_status(request, job_id):
    price_refresh_job = PriceRefreshJob.objects.filter(id=job_id).first()
    if price_refresh_job is None:
        return JsonResponse({"status": "not_found"}, status=404)
    return JsonResponse(
        {
            "id": price_refresh_job.id,
            "kind": price_refresh_job.kind,
            "status": price_refresh_job.status,
            "refreshed_count": price_refresh_job.refreshed_count,
            "error_message": price_refresh_job.error_message,
            "finished_at": price_refresh_job.finished_at.isoformat() if price_refresh_job.finished_at else None,
        }
    )
