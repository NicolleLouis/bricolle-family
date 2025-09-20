import markdown
from django.shortcuts import render
from django.utils.safestring import mark_safe

from documents.constants.directories import Directories
from documents.models import Document


def speedrun(request):
    document, _ = Document.objects.get_or_create(
        title="Balatro",
        directory=Directories.SPEEDRUN,
        defaults={"content": ""},
    )

    content_html = mark_safe(markdown.markdown(document.content))

    return render(
        request,
        "games_collection/speedrun.html",
        {"title": document.title, "content_html": content_html},
    )
