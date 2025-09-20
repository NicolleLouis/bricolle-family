from documents.constants.directories import Directories
from documents.views import render_document


class DocumentController:
    @staticmethod
    def _render_document(request, title: str):
        return render_document(
            request,
            title=title,
            directory=Directories.AGATHE,
            template_name="agathe/document.html",
        )

    @staticmethod
    def question_to_ask(request):
        return DocumentController._render_document(request, "Question à poser")

    @staticmethod
    def next_evolution_milestone(request):
        return DocumentController._render_document(request, "Next évolution milestone")

    @staticmethod
    def website_ideas(request):
        return DocumentController._render_document(request, "Website Ideas")
