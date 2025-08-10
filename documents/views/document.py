from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.utils.safestring import mark_safe
import markdown

from documents.constants.directories import Directories
from documents.forms import DocumentForm
from documents.models import Document


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
