from documents.constants.directories import Directories
from documents.views import render_document


def _render_document(request, title: str):
    return render_document(
        request,
        title=title,
        directory=Directories.FINANCE_SIMULATOR,
        template_name="finance_simulator/document.html",
    )


def ideas(request):
    return _render_document(request, "Ideas")
