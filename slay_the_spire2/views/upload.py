import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from slay_the_spire2.services.run_file_upload import RunFileUploadService
from slay_the_spire2.services.run_zip_upload import RunZipUploadService

logger = logging.getLogger(__name__)


def upload(request):
    if request.method == "POST":
        return _handle_upload(request)

    return render(request, "slay_the_spire2/upload.html")


def _handle_upload(request):
    uploaded_file = request.FILES.get("run_file")
    if not uploaded_file:
        messages.error(request, "Selectionne un fichier .run a importer.")
        return redirect("slay_the_spire2:upload")

    try:
        if uploaded_file.name.lower().endswith(".zip"):
            _handle_zip_upload(uploaded_file, request)
            return redirect("slay_the_spire2:upload")

        run_file = RunFileUploadService().upload_run_file(uploaded_file)
    except ValidationError as error:
        logger.exception(
            "Run file upload failed for '%s'.",
            uploaded_file.name,
        )
        error_message = error.message_dict.get("file", ["Le fichier est invalide."])[0]
        messages.error(request, error_message)
        return redirect("slay_the_spire2:upload")
    except ValueError as error:
        logger.exception(
            "Run file upload failed for '%s'.",
            uploaded_file.name,
        )
        messages.error(request, str(error))
        return redirect("slay_the_spire2:upload")

    messages.success(
        request,
        f"Import termine pour {run_file.original_file_name}.",
    )
    return redirect("slay_the_spire2:upload")


def _handle_zip_upload(uploaded_file, request):
    upload_result = RunZipUploadService().upload_zip_file(uploaded_file)

    if upload_result["imported_count"] > 0:
        messages.success(
            request,
            f"Import zip termine: {upload_result['imported_count']}/{upload_result['processed_files_count']} fichier(s) importe(s).",
        )

    if upload_result["error_messages"]:
        preview_errors = upload_result["error_messages"][:5]
        for error_message in preview_errors:
            messages.error(request, error_message)
        remaining_errors = len(upload_result["error_messages"]) - len(preview_errors)
        if remaining_errors > 0:
            messages.error(request, f"... et {remaining_errors} autre(s) erreur(s).")
