from django.shortcuts import get_object_or_404, redirect, render

from civilization7.forms import GameForm
from civilization7.models import Game


def recent_games(request):
    games = list(Game.objects.order_by("-created_at"))
    for g in games:
        g.form = GameForm(instance=g)
    create_form = GameForm()
    return render(
        request,
        "civilization7/recent_games.html",
        {"games": games, "create_form": create_form},
    )


def game_create(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect("civilization7:recent_games")


def game_update(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if request.method == "POST":
        form = GameForm(request.POST, instance=game)
        if form.is_valid():
            form.save()
    return redirect("civilization7:recent_games")
