from django.shortcuts import render

from slay_the_spire2.models.character import Character
from slay_the_spire2.services.boss_stats import BossStatsService


def boss(request):
    selected_character = request.GET.get("character", "all")
    selected_act = request.GET.get("act", "all")
    character_id = _parse_character_id(selected_character)
    act = _parse_act(selected_act)

    dangerousness_stats = BossStatsService().get_boss_dangerousness_stats(character_id=character_id, act=act)

    return render(
        request,
        "slay_the_spire2/boss.html",
        {
            "dangerousness_stats": dangerousness_stats,
            "character_choices": Character.objects.order_by("name"),
            "selected_character": selected_character,
            "selected_act": selected_act,
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
