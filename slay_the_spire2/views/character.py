from django.shortcuts import render

from slay_the_spire2.services.character_stats import CharacterStatsService


def character(request):
    sort_by = request.GET.get("sort")
    direction = request.GET.get("direction")
    character_stats = CharacterStatsService().get_character_stats(sort_by=sort_by, direction=direction)
    return render(
        request,
        "slay_the_spire2/character.html",
        {
            "character_stats": character_stats,
            "sort_by": sort_by or "win_number",
            "direction": direction or "desc",
        },
    )
