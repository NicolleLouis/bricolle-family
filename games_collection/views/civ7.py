from django.shortcuts import render
from django.utils.safestring import mark_safe
import markdown

from documents.constants.directories import Directories
from documents.models import Document


def civ7(request):
    docs = (
        Document.objects.filter(directory=Directories.CIVILIZATION7)
        .order_by("-updated_at")
    )
    documents = [
        {
            "title": doc.title,
            "content": mark_safe(markdown.markdown(doc.content)),
        }
        for doc in docs
    ]
    return render(request, "games_collection/civ7.html", {"documents": documents})
