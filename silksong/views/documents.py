from django.shortcuts import render
from django.utils.safestring import mark_safe
import markdown

from documents.models import Document
from documents.constants.directories import Directories


def _render_document(request, title: str, *, active_page: str):
    document, _ = Document.objects.get_or_create(
        title=title,
        directory=Directories.SILKSONG,
        defaults={"content": ""},
    )
    content_html = mark_safe(markdown.markdown(document.content))
    return render(
        request,
        "silksong/document.html",
        {
            "title": title,
            "content_html": content_html,
            "active_page": active_page,
        },
    )


def objectives(request):
    return _render_document(request, "Objectives", active_page="objectives")


def ideas(request):
    return _render_document(request, "Ideas", active_page="ideas")
