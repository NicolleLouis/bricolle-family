from django.shortcuts import render
from django.urls import reverse

def home(request):
    games = [
        {
            "name": "Back to the Dawn",
            "url": reverse("games_collection:back_to_the_dawn"),
            "color": "#8e44ad",
        },
        {
            "name": "Civ7",
            "url": reverse("games_collection:civilization_7"),
            "color": "#2C3E50",
        },
        {
            "name": "Speedrun",
            "url": reverse("games_collection:speedrun"),
            "color": "#E67E22",
        },
    ]
    return render(request, "games_collection/home.html", {"games": games})
