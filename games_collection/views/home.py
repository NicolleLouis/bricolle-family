from django.shortcuts import render
from django.urls import reverse

def home(request):
    games = [
        {
            "name": "Back to the Dawn",
            "url": reverse("games_collection:back_to_the_dawn"),
            "color": "#8e44ad",
        }
    ]
    return render(request, "games_collection/home.html", {"games": games})
