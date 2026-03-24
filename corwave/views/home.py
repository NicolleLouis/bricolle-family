from django.http import HttpResponse
from django.shortcuts import render

from corwave.services.csv_enrichment_service import (
    CorwaveCsvEnrichmentService,
    CorwaveCsvEnrichmentServiceError,
)


def home(request):
    if request.method == "POST":
        return _handle_csv_enrichment(request)

    return render(request, "corwave/home.html")


def _handle_csv_enrichment(request):
    uploaded_csv = request.FILES.get("csv_file")

    if not uploaded_csv:
        return render(
            request,
            "corwave/home.html",
            {"error_message": "Veuillez sélectionner un fichier CSV."},
        )

    service = CorwaveCsvEnrichmentService()
    try:
        enrichment_result = service.enrich_csv(
            csv_file_name=uploaded_csv.name,
            csv_file_content=uploaded_csv.read(),
        )
    except CorwaveCsvEnrichmentServiceError as service_error:
        return render(
            request,
            "corwave/home.html",
            {"error_message": str(service_error)},
        )

    response = HttpResponse(enrichment_result.content, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{enrichment_result.filename}"'
    return response
