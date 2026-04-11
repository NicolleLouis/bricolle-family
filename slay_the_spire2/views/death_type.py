from django.shortcuts import render

from slay_the_spire2.services.death_type_stats import DeathTypeStatsService


def death_type(request):
    death_type_stats = DeathTypeStatsService().get_death_type_stats()
    return render(
        request,
        "slay_the_spire2/death_type.html",
        {"death_type_stats": death_type_stats},
    )
