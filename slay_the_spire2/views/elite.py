from django.shortcuts import render

from slay_the_spire2.models.character import Character
from slay_the_spire2.services.elite_stats import EliteStatsService


def elite(request):
    selected_character = request.GET.get("character", "all")
    selected_act = request.GET.get("act", "all")
    current_tab = request.GET.get("tab", "win_rate")
    if current_tab not in {"win_rate", "dangerousness"}:
        current_tab = "win_rate"
    character_id = _parse_character_id(selected_character)
    act = _parse_act(selected_act)

    elite_service = EliteStatsService()
    global_win_rate_chart = elite_service.get_win_rate_by_elite_count_chart(character_id=character_id)
    act_1_win_rate_chart = elite_service.get_win_rate_by_elite_count_chart(character_id=character_id, act=0)
    act_2_win_rate_chart = elite_service.get_win_rate_by_elite_count_chart(character_id=character_id, act=1)
    act_3_win_rate_chart = elite_service.get_win_rate_by_elite_count_chart(character_id=character_id, act=2)
    dangerousness_stats = elite_service.get_elite_dangerousness_stats(character_id=character_id, act=act)

    return render(
        request,
        "slay_the_spire2/elite.html",
        {
            "global_win_rate_chart": global_win_rate_chart,
            "act_1_win_rate_chart": act_1_win_rate_chart,
            "act_2_win_rate_chart": act_2_win_rate_chart,
            "act_3_win_rate_chart": act_3_win_rate_chart,
            "dangerousness_stats": dangerousness_stats,
            "character_choices": Character.objects.order_by("name"),
            "selected_character": selected_character,
            "selected_act": selected_act,
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


def _parse_act(selected_act: str) -> int | None:
    if selected_act == "all":
        return None
    try:
        parsed_act = int(selected_act)
    except (TypeError, ValueError):
        return None
    if parsed_act not in {0, 1, 2}:
        return None
    return parsed_act
