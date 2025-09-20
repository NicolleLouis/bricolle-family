from documents.constants.directories import Directories
from documents.views import render_document


def _render_document(request, title: str):
    return render_document(
        request,
        title=title,
        directory=Directories.RUNETERRA,
        template_name="runeterra/document.html",
    )


def objectives(request):
    return _render_document(request, "Objectives")


def ideas(request):
    return _render_document(request, "Ideas")
