from django.shortcuts import render
from django.views.decorators.http import require_GET

from albion_online.services.aodp_request_log_service import AodpRequestLogService


@require_GET
def aodp_request_log(request):
    search_string = request.GET.get("q", "")
    request_logs = AodpRequestLogService().list_logs(search_string=search_string)
    return render(
        request,
        "albion_online/aodp_request_log.html",
        {
            "request_logs": request_logs,
            "search_string": search_string.strip(),
        },
    )
