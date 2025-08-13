from django.shortcuts import render
from django.utils.safestring import mark_safe
import markdown

from documents.constants.directories import Directories
from documents.models import Document


def civilization_7(request):
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
    return render(request, "games_collection/civilization_7.html", {"documents": documents})
