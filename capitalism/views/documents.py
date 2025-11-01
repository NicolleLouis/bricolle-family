from documents.constants.directories import Directories
from documents.views import render_document


class CapitalismDocumentView:
    template_name = "capitalism/document.html"

    @staticmethod
    def idea(request):
        return render_document(
            request,
            title="Simulation Ideas",
            directory=Directories.CAPITALISM,
            template_name=CapitalismDocumentView.template_name,
            include_edit_url=True,
        )
