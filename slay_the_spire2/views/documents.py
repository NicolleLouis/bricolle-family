from documents.constants.directories import Directories
from documents.views import render_document


class DocumentController:
    @staticmethod
    def ideas(request):
        return render_document(
            request,
            title="Ideas",
            directory=Directories.STS,
            template_name="slay_the_spire2/document.html",
        )
