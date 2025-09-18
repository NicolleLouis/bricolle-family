from django.shortcuts import render
from django.urls import reverse


def home(request):
    pages = [
        {
            "name": "Speedrun",
            "description": "Suivez vos dernières tentatives de speedrun.",
            "url": reverse("silksong:speedrun_sessions"),
        },
        {
            "name": "Steel Soul",
            "description": "Gardez un œil sur vos runs Steel Soul.",
            "url": reverse("silksong:steel_soul_sessions"),
        },
        {
            "name": "Boss Fight",
            "description": "Analysez vos affrontements contre les boss.",
            "url": reverse("silksong:boss_fight_sessions"),
        },
    ]
    return render(
        request,
        "silksong/home.html",
        {"pages": pages, "active_page": "home"},
    )
