from django.shortcuts import redirect, render

from chess.forms import GameForm
from chess.models import Game, Opening


def home(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("chess:home")
    else:
        form = GameForm()

    games = Game.objects.select_related("opening").order_by("-id")
    openings = Opening.objects.order_by("name")
    selected_opening = request.GET.get("opening") or ""
    selected_color = request.GET.get("color") or ""

    if selected_opening:
        games = games.filter(opening_id=selected_opening)
    if selected_color:
        games = games.filter(color=selected_color)

    return render(
        request,
        "chess/home.html",
        {
            "form": form,
            "games": games,
            "openings": openings,
            "selected_opening": selected_opening,
            "selected_color": selected_color,
        },
    )
