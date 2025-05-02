from django.shortcuts import render

from northguard.models.clan import ClanAdmin, Clan


def home(request):
    clans = Clan.objects.all()
    return render(
        request,
        "northguard/home.html",
        {"clans": clans}
    )
