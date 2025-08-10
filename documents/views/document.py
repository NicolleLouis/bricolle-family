from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.utils.safestring import mark_safe

try:
    import markdown
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    markdown = None

from documents.forms import DocumentForm
from documents.models import Document, Game


def document_list(request):
    documents = Document.objects.all().order_by("title")

    game = request.GET.get("game")
    query = request.GET.get("q")

    if game:
        documents = documents.filter(game=game)
    if query:
        documents = documents.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    return render(
        request,
        "documents/document_list.html",
        {"documents": documents, "games": Game},
    )


def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if markdown:
        content_html = mark_safe(markdown.markdown(document.content))
    else:  # fallback if markdown package is unavailable
        content_html = mark_safe(document.content.replace("\n", "<br>"))
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
