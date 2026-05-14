import time
from datetime import timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.constants.gathering_gear import (
    GATHERING_GEAR_DEFAULT_CITY_FILTER,
    GATHERING_GEAR_DEFAULT_RESOURCE_FILTER,
    GATHERING_GEAR_RESOURCE_FILTER_OPTIONS,
    GATHERING_GEAR_RESOURCE_GROUPS,
    GATHERING_GEAR_RESOURCE_GROUPS_BY_KEY,
    GATHERING_GEAR_VARIANT_COLUMNS,
)
from albion_online.models import GatheringGearProfitabilityDoneCraft, Object, Recipe
from albion_online.services.gathering_gear_market_summary import (
    GatheringGearMarketSummaryService,
)
from albion_online.services.gathering_gear_price_refresh import (
    GatheringGearPriceRefreshService,
)
from albion_online.services.gathering_gear_profitability import (
    GatheringGearProfitabilityService,
)


DEFAULT_MINIMUM_PERCENTAGE_FILTER = 20.0
DEFAULT_SORT_BY_FILTER = "percentage"
ALL_CITY_FILTER = "all"
DEFAULT_CITY_FILTER = GATHERING_GEAR_DEFAULT_CITY_FILTER
SORT_BY_OPTIONS = (
    {"value": "percentage", "label": "Profit %"},
    {"value": "flat", "label": "Flat amount"},
)
CACHE_VERSION_KEY = "albion_online:gathering_gear:version"
CACHED_GEAR_ROWS_KEY = "albion_online:gathering_gear:gear_rows:{version}:{resource}"
CACHED_PROFITABLE_ROWS_KEY = (
    "albion_online:gathering_gear:profitable_rows:{version}:{resource}:{city}:{min_percentage}:{min_flat}:{sort}:{done_signature}"
)
CACHED_DETAIL_GROUP_KEY = "albion_online:gathering_gear:detail_group:{version}:{detail_key}:{city}"
GATHERING_GEAR_DONE_WINDOW = timedelta(hours=12)


def _build_gathering_gear_rows(selected_resource_filter):
    selected_resource_groups = _build_selected_resource_groups(selected_resource_filter)
    gear_filter = Q()
    for resource_group in selected_resource_groups:
        gear_filter |= Q(aodp_id__contains=resource_group["aodp_id_fragment"])

    gathering_gear_objects = (
        Object.objects.filter(gear_filter, tier__gte=4)
        .select_related("type")
        .prefetch_related(
            "prices",
            Prefetch(
                "output_recipes",
                queryset=Recipe.objects.prefetch_related("inputs__object__prices"),
            ),
        )
    )
    gear_rows = GatheringGearMarketSummaryService().build_rows(gathering_gear_objects)
    return gear_rows


def _build_selected_resource_groups(selected_resource_filter):
    resource_group = GATHERING_GEAR_RESOURCE_GROUPS_BY_KEY.get(selected_resource_filter)
    if resource_group is not None:
        return (resource_group,)
    return (GATHERING_GEAR_RESOURCE_GROUPS_BY_KEY[GATHERING_GEAR_DEFAULT_RESOURCE_FILTER],)


def _get_cache_version():
    cache_version = cache.get(CACHE_VERSION_KEY)
    if cache_version is None:
        cache_version = "initial"
        cache.set(CACHE_VERSION_KEY, cache_version, None)
    return cache_version


def _invalidate_gathering_gear_cache():
    cache.set(CACHE_VERSION_KEY, str(time.time()), None)


def _get_cached_gathering_gear_rows(selected_resource_filter):
    cache_version = _get_cache_version()
    cache_key = CACHED_GEAR_ROWS_KEY.format(version=cache_version, resource=selected_resource_filter)
    gear_rows = cache.get(cache_key)
    if gear_rows is None:
        gear_rows = _build_gathering_gear_rows(selected_resource_filter)
        cache.set(cache_key, gear_rows, None)
    return gear_rows


def _get_cached_profitable_rows(
    gear_rows,
    selected_city_filter,
    selected_resource_filter,
    minimum_percentage_filter,
    minimum_flat_filter,
    selected_sort_by_filter,
    recently_done_keys,
    done_signature,
):
    cache_version = _get_cache_version()
    cache_key = CACHED_PROFITABLE_ROWS_KEY.format(
        version=cache_version,
        resource=selected_resource_filter,
        city=selected_city_filter,
        min_percentage=minimum_percentage_filter,
        min_flat=minimum_flat_filter,
        sort=selected_sort_by_filter,
        done_signature=done_signature,
    )
    profitable_rows = cache.get(cache_key)
    if profitable_rows is None:
        profitable_rows = GatheringGearProfitabilityService().build_rows(
            gear_rows,
            selected_city_filter=selected_city_filter,
            selected_gear_type_filter=selected_resource_filter,
            minimum_percentage=minimum_percentage_filter,
            minimum_flat=minimum_flat_filter,
            sort_by=selected_sort_by_filter,
            recently_done_keys=recently_done_keys,
        )
        cache.set(cache_key, profitable_rows, None)
    return profitable_rows


def _find_gear_type(aodp_id):
    for gear_type in GATHERING_GEAR_RESOURCE_GROUPS:
        if gear_type["aodp_id_fragment"] in aodp_id:
            return gear_type
    return {"key": "unknown", "label": "Unknown", "aodp_id_fragment": ""}


def _build_city_tables(gear_rows, selected_city_filter=DEFAULT_CITY_FILTER):
    table_rows_by_city = []
    notations = sorted(
        {gear_row["object"].tier_enchantment_notation for gear_row in gear_rows},
        key=_sort_notation,
    )
    rows_by_notation_and_type = {
        (gear_row["object"].tier_enchantment_notation, gear_row["object"].type_code): gear_row
        for gear_row in gear_rows
    }

    for city, city_label in _build_city_choices(selected_city_filter):
        rows = []
        for notation in notations:
            cells = []
            first_gear_row = None
            for variant_column in GATHERING_GEAR_VARIANT_COLUMNS:
                gear_row = rows_by_notation_and_type.get((notation, variant_column["object_type"]))
                city_summary = _find_city_summary(gear_row, city) if gear_row else None
                if gear_row is not None and first_gear_row is None:
                    first_gear_row = gear_row
                cells.append(
                    {
                        "gear_row": gear_row,
                        "variant_column": variant_column,
                        "city_summary": city_summary,
                    }
                )
            if first_gear_row is not None:
                detail_key = first_gear_row["detail_key"]
                detail_title = first_gear_row["object"].display_name
            else:
                detail_key = f"{selected_city_filter}:{notation}"
                detail_title = f"T{notation} Gathering Gear"
            rows.append(
                {
                    "notation": notation,
                    "display_notation": f"T{notation}",
                    "detail_key": detail_key,
                    "detail_title": detail_title,
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


def _build_selected_resource_filter(request):
    selected_resource_filter = request.GET.get("resource", GATHERING_GEAR_DEFAULT_RESOURCE_FILTER)
    if selected_resource_filter in GATHERING_GEAR_RESOURCE_GROUPS_BY_KEY:
        return selected_resource_filter
    return GATHERING_GEAR_DEFAULT_RESOURCE_FILTER


def _build_selected_resource_filter_for_profitability(request):
    selected_resource_filter = request.GET.get("resource", GATHERING_GEAR_DEFAULT_RESOURCE_FILTER)
    if selected_resource_filter in GATHERING_GEAR_RESOURCE_GROUPS_BY_KEY:
        return selected_resource_filter
    return GATHERING_GEAR_DEFAULT_RESOURCE_FILTER


def _build_resource_filter_options():
    return list(GATHERING_GEAR_RESOURCE_FILTER_OPTIONS)


def _build_city_filter_options():
    return [
        {"value": ALL_CITY_FILTER, "label": "All"},
        *[{"value": city, "label": city_label} for city, city_label in City.choices],
    ]


def _find_city_summary(gear_row, city):
    for city_summary in gear_row["city_summaries"]:
        if city_summary.city == city:
            return city_summary
    return None


def _sort_notation(notation):
    if notation is None:
        return (0, 0)
    tier, enchantment = notation.split(".")
    return (int(tier), int(enchantment))


def _build_minimum_percentage_filter(request):
    raw_value = request.GET.get("min_percentage", str(DEFAULT_MINIMUM_PERCENTAGE_FILTER))
    try:
        return float(raw_value.replace(",", "."))
    except (AttributeError, ValueError):
        return DEFAULT_MINIMUM_PERCENTAGE_FILTER


def _build_minimum_flat_filter(request):
    raw_value = request.GET.get("min_flat", "").strip()
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except ValueError:
        return None


def _build_selected_sort_by_filter(request):
    selected_sort_by = request.GET.get("sort", DEFAULT_SORT_BY_FILTER)
    if selected_sort_by in {option["value"] for option in SORT_BY_OPTIONS}:
        return selected_sort_by
    return DEFAULT_SORT_BY_FILTER


def _build_recently_done_craft_state(selected_city_filter, selected_resource_filter):
    cutoff = timezone.now() - GATHERING_GEAR_DONE_WINDOW
    done_crafts = (
        GatheringGearProfitabilityDoneCraft.objects.select_related("object")
        .filter(completed_at__gte=cutoff)
        .order_by("city", "object__aodp_id", "completed_at", "pk")
    )

    if selected_city_filter != ALL_CITY_FILTER:
        done_crafts = done_crafts.filter(city=selected_city_filter)

    selected_resource_groups = _build_selected_resource_groups(selected_resource_filter)
    selected_resource_query = Q()
    for resource_group in selected_resource_groups:
        selected_resource_query |= Q(object__aodp_id__contains=resource_group["aodp_id_fragment"])
    done_crafts = done_crafts.filter(selected_resource_query)

    recently_done_keys = {
        (done_craft.city, done_craft.object_id)
        for done_craft in done_crafts
    }
    done_signature = "|".join(
        f"{done_craft.city}:{done_craft.object.aodp_id}:{done_craft.completed_at.isoformat()}"
        for done_craft in done_crafts
    ) or "none"
    return recently_done_keys, done_signature


def _build_profitability_refresh_redirect(
    selected_city_filter,
    selected_resource_filter,
    minimum_percentage_filter,
    minimum_flat_filter,
    selected_sort_by_filter,
):
    query_string = _build_query_string(
        city=selected_city_filter,
        resource=selected_resource_filter,
        min_percentage=minimum_percentage_filter,
        min_flat=minimum_flat_filter,
        sort=selected_sort_by_filter,
    )
    redirect_url = reverse("albion_online:gathering_gear_profitability")
    if query_string:
        return f"{redirect_url}?{query_string}"
    return redirect_url


def _build_query_string(**query_params):
    filtered_query_params = {key: value for key, value in query_params.items() if value not in (None, "")}
    return urlencode(filtered_query_params)


def _refresh_prices_and_redirect(request, redirect_url_name, **query_params):
    selected_resource_filter = query_params.get("resource", GATHERING_GEAR_DEFAULT_RESOURCE_FILTER)
    created_prices = GatheringGearPriceRefreshService().refresh_prices(selected_resource_filter=selected_resource_filter)
    _invalidate_gathering_gear_cache()
    messages.success(
        request,
        f"{len(created_prices)} price entries refreshed for gathering gear.",
    )
    query_string = _build_query_string(**query_params)
    redirect_url = reverse(redirect_url_name)
    if query_string:
        return redirect(f"{redirect_url}?{query_string}")
    return redirect(redirect_url)


def gathering_gear(request):
    selected_city_filter = _build_selected_city_filter(request)
    selected_resource_filter = _build_selected_resource_filter(request)
    if request.method == "POST":
        return _refresh_prices_and_redirect(
            request,
            "albion_online:gathering_gear",
            city=selected_city_filter,
            resource=selected_resource_filter,
        )

    gear_rows = _get_cached_gathering_gear_rows(selected_resource_filter)
    return render(
        request,
        "albion_online/gathering_gear.html",
        {
            "city_filter_options": _build_city_filter_options(),
            "resource_filter_options": _build_resource_filter_options(),
            "city_tables": _build_city_tables(gear_rows, selected_city_filter),
            "gear_rows": gear_rows,
            "gear_variant_columns": GATHERING_GEAR_VARIANT_COLUMNS,
            "selected_city_filter": selected_city_filter,
            "selected_resource_filter": selected_resource_filter,
            "selected_resource_label": GATHERING_GEAR_RESOURCE_GROUPS_BY_KEY[selected_resource_filter]["label"],
            "detail_panel_url": reverse("albion_online:gathering_gear_detail_panel"),
            "table_columns_count": len(GATHERING_GEAR_VARIANT_COLUMNS) + 1,
        },
    )


def gathering_gear_profitability(request):
    selected_city_filter = _build_selected_city_filter(request)
    selected_resource_filter = _build_selected_resource_filter_for_profitability(request)
    minimum_percentage_filter = _build_minimum_percentage_filter(request)
    minimum_flat_filter = _build_minimum_flat_filter(request)
    selected_sort_by_filter = _build_selected_sort_by_filter(request)
    recently_done_keys, done_signature = _build_recently_done_craft_state(
        selected_city_filter,
        selected_resource_filter,
    )

    if request.method == "POST":
        return _refresh_prices_and_redirect(
            request,
            "albion_online:gathering_gear_profitability",
            city=selected_city_filter,
            resource=selected_resource_filter,
            min_percentage=minimum_percentage_filter,
            min_flat=minimum_flat_filter,
            sort=selected_sort_by_filter,
        )

    gear_rows = _get_cached_gathering_gear_rows(selected_resource_filter)
    profitable_rows = _get_cached_profitable_rows(
        gear_rows,
        selected_city_filter,
        selected_resource_filter,
        minimum_percentage_filter,
        minimum_flat_filter,
        selected_sort_by_filter,
        recently_done_keys,
        done_signature,
    )
    return render(
        request,
        "albion_online/gathering_gear_profitability.html",
        {
            "city_filter_options": _build_city_filter_options(),
            "minimum_flat_filter": minimum_flat_filter,
            "minimum_percentage_filter": minimum_percentage_filter,
            "refresh_query_string": _build_query_string(
                city=selected_city_filter,
                resource=selected_resource_filter,
                min_percentage=minimum_percentage_filter,
                min_flat=minimum_flat_filter,
                sort=selected_sort_by_filter,
            ),
            "profitable_rows": profitable_rows,
            "detail_panel_url": reverse("albion_online:gathering_gear_detail_panel"),
            "selected_city_filter": selected_city_filter,
            "selected_resource_filter": selected_resource_filter,
            "selected_sort_by_filter": selected_sort_by_filter,
            "sort_by_options": SORT_BY_OPTIONS,
        },
    )


def gathering_gear_mark_done(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    object_aodp_id = request.POST.get("object_aodp_id")
    row_city = request.POST.get("row_city")
    if not object_aodp_id or row_city not in City.values:
        return HttpResponseNotFound("Missing profitability craft identifiers.")

    gear_object = Object.objects.filter(aodp_id=object_aodp_id).first()
    if gear_object is None:
        return HttpResponseNotFound("Craft not found.")

    GatheringGearProfitabilityDoneCraft.objects.update_or_create(
        object=gear_object,
        city=row_city,
        defaults={
            "completed_at": timezone.now(),
        },
    )
    _invalidate_gathering_gear_cache()
    messages.success(request, "Craft marked as done for 12 hours.")
    return redirect(
        _build_profitability_refresh_redirect(
            _build_selected_city_filter(request),
            _build_selected_resource_filter_for_profitability(request),
            _build_minimum_percentage_filter(request),
            _build_minimum_flat_filter(request),
            _build_selected_sort_by_filter(request),
        )
    )


def gathering_gear_detail_panel(request):
    detail_key = request.GET.get("detail_key")
    if not detail_key:
        return HttpResponseNotFound("Missing detail key.")

    selected_city_filter = request.GET.get("city", ALL_CITY_FILTER)
    if selected_city_filter != ALL_CITY_FILTER and selected_city_filter not in City.values:
        selected_city_filter = ALL_CITY_FILTER

    cache_version = _get_cache_version()
    cache_key = CACHED_DETAIL_GROUP_KEY.format(
        version=cache_version,
        detail_key=detail_key,
        city=selected_city_filter,
    )
    cached_html = cache.get(cache_key)
    if cached_html is not None:
        return HttpResponse(cached_html)

    selected_resource_filter = detail_key.split(":", 1)[0]
    gear_rows = _get_cached_gathering_gear_rows(selected_resource_filter)
    gear_row = next((row for row in gear_rows if row["detail_key"] == detail_key), None)
    if gear_row is None:
        return HttpResponseNotFound("Detail not found.")

    detail_html = render_to_string(
        "albion_online/gathering_gear_detail_group.html",
        {
            "gear_row": gear_row,
            "selected_city_filter": selected_city_filter,
        },
        request=request,
    )
    cache.set(cache_key, detail_html, None)
    return HttpResponse(detail_html)
