from django.shortcuts import render
from django.utils.safestring import mark_safe
import markdown

from documents.models import Document
from documents.constants.directories import Directories


class DocumentController:
    @staticmethod
    def _render_document(request, title: str):
        document, _ = Document.objects.get_or_create(
            title=title,
            directory=Directories.AGATHER,
            defaults={"content": ""},
        )
        content_html = mark_safe(markdown.markdown(document.content))
        return render(
            request,
            "agathe/document.html",
            {"title": title, "content_html": content_html, "document": document},
        )

    @staticmethod
    def question_to_ask(request):
        return DocumentController._render_document(request, "Question à poser")

    @staticmethod
    def next_evolution_milestone(request):
        return DocumentController._render_document(request, "Next évolution milestone")

