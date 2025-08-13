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
            "url": reverse("games_collection:civ7"),
            "color": "#2C3E50",
        },
    ]
    return render(request, "games_collection/home.html", {"games": games})
