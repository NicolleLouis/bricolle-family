from urllib.parse import urlencode

from django.shortcuts import render
from django.urls import reverse
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
    redirect_to = request.get_full_path()
    edit_url = reverse("documents:document_edit", args=[document.pk])
    if redirect_to:
        edit_url = f"{edit_url}?{urlencode({'next': redirect_to})}"
    return render(
        request,
        "silksong/document.html",
        {
            "title": title,
            "content_html": content_html,
            "active_page": active_page,
            "edit_url": edit_url,
        },
    )


def objectives(request):
    return _render_document(request, "Objectives", active_page="objectives")


def ideas(request):
    return _render_document(request, "Ideas", active_page="ideas")
