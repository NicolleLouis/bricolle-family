from typing import Any, Dict, Optional

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.utils.safestring import mark_safe
import markdown
from urllib.parse import urlencode

from documents.constants.directories import Directories
from documents.forms import DocumentForm
from documents.models import Document


DEFAULT_REDIRECT_FIELD_NAME = "next"


def render_document(
    request,
    *,
    title: str,
    directory: Directories,
    template_name: str,
    extra_context: Optional[Dict[str, Any]] = None,
    include_edit_url: bool = False,
    redirect_to: Optional[str] = None,
    redirect_field_name: str = DEFAULT_REDIRECT_FIELD_NAME,
):
    """Render a document page by loading Markdown content and optional edit link."""

    document, _ = Document.objects.get_or_create(
        title=title,
        directory=directory,
        defaults={"content": ""},
    )
    content_html = mark_safe(markdown.markdown(document.content))

    context: Dict[str, Any] = {
        "title": title,
        "content_html": content_html,
        "document": document,
    }
    if extra_context:
        context.update(extra_context)

    if include_edit_url:
        if redirect_to is None:
            redirect_to = request.get_full_path()
        edit_url = reverse("documents:document_edit", args=[document.pk])
        if redirect_to:
            edit_url = f"{edit_url}?{urlencode({redirect_field_name: redirect_to})}"
        context["edit_url"] = edit_url

    return render(request, template_name, context)


def document_list(request):
    documents = Document.objects.all().order_by("title")

    directory = request.GET.get("directory")
    query = request.GET.get("q")

    if directory:
        documents = documents.filter(directory=directory)
    if query:
        documents = documents.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    return render(
        request,
        "documents/document_list.html",
        {"documents": documents, "directories": Directories},
    )


def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    content_html = mark_safe(markdown.markdown(document.content))
    return render(
        request,
        "documents/document_detail.html",
        {"document": document, "content_html": content_html},
    )


class DocumentCreateView(CreateView):
    model = Document
    form_class = DocumentForm
    template_name = "documents/document_form.html"
    success_url = reverse_lazy("documents:document_list")


class DocumentUpdateView(UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = "documents/document_form.html"
    success_url = reverse_lazy("documents:document_list")
    redirect_field_name = DEFAULT_REDIRECT_FIELD_NAME

    def _get_redirect_to(self):
        return self.request.POST.get(self.redirect_field_name) or self.request.GET.get(
            self.redirect_field_name
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        redirect_to = self._get_redirect_to()
        if redirect_to:
            context["redirect_to"] = redirect_to
            context["redirect_field_name"] = self.redirect_field_name
        return context

    def get_success_url(self):
        redirect_to = self._get_redirect_to()
        if redirect_to:
            return redirect_to
        return super().get_success_url()
