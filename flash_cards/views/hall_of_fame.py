from __future__ import annotations

from typing import Mapping

from django.shortcuts import render

from flash_cards.models import Category
from flash_cards.services import HallOfFameService, HardQuestion


def hall_of_fame(request):
    category_id = _parse_category_id(request.GET.get("category"))
    service = HallOfFameService()
    entries = tuple(
        _serialize_entry(entry)
        for entry in service.get_hardest_questions(category_id=category_id)
    )
    categories = Category.objects.all()
    return render(
        request,
        "flash_cards/hall_of_fame.html",
        {
            "entries": entries,
            "categories": categories,
            "selected_category": category_id,
        },
    )


def _parse_category_id(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _serialize_entry(entry: HardQuestion) -> Mapping[str, object]:
    success_percentage = round(entry.success_rate * 100)
    return {
        "question": entry.question,
        "success_percentage": success_percentage,
        "success_color": _success_color(entry.success_rate),
        "failure_count": entry.failure_count,
    }


def _success_color(rate: float) -> str:
    clamped = max(0.0, min(rate, 1.0))
    hue = int(clamped * 120)
    return f"hsl({hue}, 70%, 45%)"
