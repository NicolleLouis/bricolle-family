from django.shortcuts import render
from django.utils.safestring import mark_safe
import markdown

from documents.models import Document
from documents.constants.directories import Directories


def _render_document(request, title: str):
    document, _ = Document.objects.get_or_create(
        title=title,
        directory=Directories.RUNETERRA,
        defaults={"content": ""},
    )
    content_html = mark_safe(markdown.markdown(document.content))
    return render(
        request,
        "runeterra/document.html",
        {"title": title, "content_html": content_html},
    )


def objectives(request):
    return _render_document(request, "Objectives")


def ideas(request):
    return _render_document(request, "Ideas")
