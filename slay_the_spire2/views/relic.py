from django.shortcuts import render

from slay_the_spire2.models.character import Character
from slay_the_spire2.services.relic_stats import RelicStatsService


def relic(request):
    sort_by = request.GET.get("sort")
    direction = request.GET.get("direction")
    selected_character = request.GET.get("character", "all")
    current_tab = request.GET.get("tab", "general")
    if current_tab not in {"general", "win_by_relic_number"}:
        current_tab = "general"
    character_id = _parse_character_id(selected_character)

    relic_service = RelicStatsService()
    relic_stats = relic_service.get_relic_stats(
        sort_by=sort_by,
        direction=direction,
        character_id=character_id,
    )
    win_by_relic_number_chart = relic_service.get_win_by_relic_number_chart(character_id=character_id)
    return render(
        request,
        "slay_the_spire2/relic.html",
        {
            "relic_stats": relic_stats,
            "win_by_relic_number_chart": win_by_relic_number_chart,
            "sort_by": sort_by or "win_number",
            "direction": direction or "desc",
            "character_choices": Character.objects.order_by("name"),
            "selected_character": selected_character,
            "current_tab": current_tab,
        },
    )


def _parse_character_id(selected_character: str) -> int | None:
    if selected_character == "all":
        return None
    try:
        return int(selected_character)
    except (TypeError, ValueError):
        return None
