from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from chess.forms import OpeningForm
from chess.models import Opening


def openings_config(request):
    if request.method == "POST":
        opening_id = request.POST.get("opening_id")
        if opening_id:
            opening = get_object_or_404(Opening, pk=opening_id)
            form = OpeningForm(request.POST, instance=opening, prefix=str(opening.id))
        else:
            form = OpeningForm(request.POST, prefix="create")
        if form.is_valid():
            form.save()
        return redirect("chess:openings")

    openings = list(Opening.objects.annotate(game_count=Count("games")).order_by("name"))
    openings_with_forms = [
        {
            "opening": opening,
            "form": OpeningForm(instance=opening, prefix=str(opening.id)),
        }
        for opening in openings
    ]
    create_form = OpeningForm(prefix="create")
    return render(
        request,
        "chess/openings.html",
        {
            "openings": openings_with_forms,
            "create_form": create_form,
        },
    )
