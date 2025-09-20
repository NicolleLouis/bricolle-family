from documents.constants.directories import Directories
from documents.views import render_document


def _render_document(request, title: str, *, active_page: str):
    return render_document(
        request,
        title=title,
        directory=Directories.SILKSONG,
        template_name="silksong/document.html",
        extra_context={"active_page": active_page},
        include_edit_url=True,
    )


def objectives(request):
    return _render_document(request, "Objectives", active_page="objectives")


def ideas(request):
    return _render_document(request, "Ideas", active_page="ideas")
