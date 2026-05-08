from django.contrib import messages
from django.db.models import Q
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.urls import reverse

from albion_online.constants.city import City
from albion_online.constants.leather_jacket import LEATHER_JACKET_TYPES
from albion_online.models import Object, Recipe
from albion_online.services.mercenary_jacket_market_summary import (
    MercenaryJacketMarketSummaryService,
)
from albion_online.services.mercenary_jacket_price_refresh import (
    LeatherJacketPriceRefreshService,
)


ALL_CITY_FILTER = "all"
DEFAULT_CITY_FILTER = City.FORT_STERLING


def _build_leather_jacket_rows():
    jacket_filter = Q()
    for jacket_type in LEATHER_JACKET_TYPES:
        jacket_filter |= Q(aodp_id__contains=jacket_type["aodp_id_fragment"])

    leather_jackets = (
        Object.objects.filter(jacket_filter, tier__gte=4)
        .select_related("type")
        .prefetch_related(
            "prices",
            Prefetch(
                "output_recipes",
                queryset=Recipe.objects.prefetch_related("inputs__object__prices"),
            ),
        )
    )
    jacket_rows = MercenaryJacketMarketSummaryService().build_rows(leather_jackets)
    for jacket_row in jacket_rows:
        jacket_type = _find_jacket_type(jacket_row["object"].aodp_id)
        jacket_row["jacket_type"] = jacket_type
        jacket_row["jacket_type_key"] = jacket_type["key"]
        jacket_row["jacket_type_label"] = jacket_type["label"]
        jacket_row["detail_key"] = f"{jacket_type['key']}:{jacket_row['object'].tier_enchantment_notation}"
    return jacket_rows


def _find_jacket_type(aodp_id):
    for jacket_type in LEATHER_JACKET_TYPES:
        if jacket_type["aodp_id_fragment"] in aodp_id:
            return jacket_type
    return {"key": "unknown", "label": "Unknown", "aodp_id_fragment": ""}


def _build_city_tables(jacket_rows, selected_city_filter=DEFAULT_CITY_FILTER):
    table_rows_by_city = []
    notations = sorted(
        {jacket_row["object"].tier_enchantment_notation for jacket_row in jacket_rows},
        key=_sort_notation,
    )
    rows_by_notation_and_type = {
        (jacket_row["object"].tier_enchantment_notation, jacket_row["jacket_type_key"]): jacket_row
        for jacket_row in jacket_rows
    }

    for city, city_label in _build_city_choices(selected_city_filter):
        rows = []
        for notation in notations:
            cells = []
            row_input_details = []
            output_details = []
            for jacket_type in LEATHER_JACKET_TYPES:
                jacket_row = rows_by_notation_and_type.get((notation, jacket_type["key"]))
                city_summary = _find_city_summary(jacket_row, city) if jacket_row else None
                city_detail = _find_city_detail(jacket_row, city) if jacket_row else None
                if city_detail is not None and not row_input_details:
                    row_input_details = city_detail.input_details
                if jacket_row is not None and city_detail is not None:
                    output_details.append(
                        {
                            "jacket_row": jacket_row,
                            "jacket_type": jacket_type,
                            "city_detail": city_detail,
                        }
                    )
                cells.append(
                    {
                        "jacket_row": jacket_row,
                        "jacket_type": jacket_type,
                        "city_summary": city_summary,
                    }
                )
            rows.append(
                {
                    "notation": notation,
                    "display_notation": f"T{notation}",
                    "detail_key": f"{city}:{notation}",
                    "detail_title": f"T{notation} Leather Jackets",
                    "input_details": row_input_details,
                    "output_details": output_details,
                    "cells": cells,
                }
            )
        table_rows_by_city.append({"city": city, "label": city_label, "rows": rows})
    return table_rows_by_city


def _build_city_choices(selected_city_filter):
    if selected_city_filter == ALL_CITY_FILTER:
        return City.choices
    return [(city, city_label) for city, city_label in City.choices if city == selected_city_filter]


def _build_selected_city_filter(request):
    selected_city_filter = request.GET.get("city", DEFAULT_CITY_FILTER)
    if selected_city_filter == ALL_CITY_FILTER:
        return ALL_CITY_FILTER
    if selected_city_filter in City.values:
        return selected_city_filter
    return DEFAULT_CITY_FILTER


def _build_city_filter_options():
    return [
        {"value": ALL_CITY_FILTER, "label": "All"},
        *[{"value": city, "label": city_label} for city, city_label in City.choices],
    ]


def _find_city_summary(jacket_row, city):
    for city_summary in jacket_row["city_summaries"]:
        if city_summary.city == city:
            return city_summary
    return None


def _find_city_detail(jacket_row, city):
    for city_detail in jacket_row["city_details"]:
        if city_detail.city == city:
            return city_detail
    return None


def _sort_notation(notation):
    if notation is None:
        return (0, 0)
    tier, enchantment = notation.split(".")
    return (int(tier), int(enchantment))


def leather_jacket(request):
    selected_city_filter = _build_selected_city_filter(request)
    if request.method == "POST":
        created_prices = LeatherJacketPriceRefreshService().refresh_prices()
        messages.success(
            request,
            f"{len(created_prices)} price entries refreshed for leather jackets.",
        )
        return redirect(f"{reverse('albion_online:leather_jacket')}?city={selected_city_filter}")

    jacket_rows = _build_leather_jacket_rows()
    return render(
        request,
        "albion_online/leather_jacket.html",
        {
            "city_filter_options": _build_city_filter_options(),
            "city_tables": _build_city_tables(jacket_rows, selected_city_filter),
            "jacket_rows": jacket_rows,
            "jacket_types": LEATHER_JACKET_TYPES,
            "selected_city_filter": selected_city_filter,
            "table_columns_count": len(LEATHER_JACKET_TYPES) + 1,
        },
    )
