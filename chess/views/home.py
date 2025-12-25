from django.shortcuts import redirect, render

from chess.forms import GameForm


def home(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("chess:home")
    else:
        form = GameForm()

    return render(request, "chess/home.html", {"form": form})
