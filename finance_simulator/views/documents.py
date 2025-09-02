from django.shortcuts import render
from django.utils.safestring import mark_safe
import markdown

from documents.models import Document
from documents.constants.directories import Directories


def _render_document(request, title: str):
    document, _ = Document.objects.get_or_create(
        title=title,
        directory=Directories.FINANCE_SIMULATOR,
        defaults={"content": ""},
    )
    content_html = mark_safe(markdown.markdown(document.content))
    return render(
        request,
        "finance_simulator/document.html",
        {"title": title, "content_html": content_html, "document": document},
    )


def ideas(request):
    return _render_document(request, "Ideas")
