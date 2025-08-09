from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from games_collection.forms.markdown_document import MarkdownDocumentForm
from games_collection.models import MarkdownDocument, Game


def markdown_document_list(request):
    documents = MarkdownDocument.objects.all().order_by("title")

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
        "games_collection/markdown_document_list.html",
        {"documents": documents, "games": Game},
    )


class MarkdownDocumentCreateView(CreateView):
    model = MarkdownDocument
    form_class = MarkdownDocumentForm
    template_name = "games_collection/markdown_document_form.html"
    success_url = reverse_lazy("games_collection:markdown_document_list")


class MarkdownDocumentUpdateView(UpdateView):
    model = MarkdownDocument
    form_class = MarkdownDocumentForm
    template_name = "games_collection/markdown_document_form.html"
    success_url = reverse_lazy("games_collection:markdown_document_list")
