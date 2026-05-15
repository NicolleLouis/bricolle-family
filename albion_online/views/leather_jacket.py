from django.contrib import messages
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from urllib.parse import urlencode

from albion_online.constants.city import City
from albion_online.constants.leather_jacket import LEATHER_JACKET_TYPES
from albion_online.models import Object, PriceRefreshJob
from albion_online.services.leather_jacket_profitability import (
    LeatherJacketProfitabilityService,
)
from albion_online.services.craft_profitability_done import (
    CraftProfitabilityDoneService,
)
from albion_online.services.mercenary_jacket_market_summary import (
    MercenaryJacketMarketSummaryService,
)
from albion_online.services.market_summary_querysets import (
    build_market_summary_object_queryset,
)
from albion_online.tasks import refresh_price_job


ALL_CITY_FILTER = "all"
ALL_JACKET_TYPE_FILTER = "all"
DEFAULT_MINIMUM_PERCENTAGE_FILTER = 20.0
DEFAULT_SORT_BY_FILTER = "percentage"
DEFAULT_CITY_FILTER = City.FORT_STERLING
SORT_BY_OPTIONS = (
    {"value": "percentage", "label": "Profit %"},
    {"value": "flat", "label": "Flat amount"},
)
CACHE_VERSION_KEY = "albion_online:leather_jacket:version"
CACHE_PAYLOAD_VERSION = "v2"
CACHED_JACKET_ROWS_KEY = f"albion_online:leather_jacket:jacket_rows:{{version}}:{CACHE_PAYLOAD_VERSION}"
CACHED_PROFITABLE_ROWS_KEY = (
    f"albion_online:leather_jacket:profitable_rows:{{version}}:{CACHE_PAYLOAD_VERSION}:{{city}}:{{jacket_type}}:{{min_percentage}}:{{min_flat}}:{{sort}}:{{done_signature}}"
)
CACHED_DETAIL_GROUP_KEY = "albion_online:leather_jacket:detail_group:{version}:{detail_key}:{city}"


def _build_leather_jacket_rows():
    jacket_filter = Q()
    for jacket_type in LEATHER_JACKET_TYPES:
        jacket_filter |= Q(aodp_id__contains=jacket_type["aodp_id_fragment"])

    leather_jackets = build_market_summary_object_queryset(
        Object.objects.filter(jacket_filter, tier__gte=4)
    )
    jacket_rows = MercenaryJacketMarketSummaryService().build_rows(leather_jackets)
    for jacket_row in jacket_rows:
        jacket_type = _find_jacket_type(jacket_row["object"].aodp_id)
        jacket_row["jacket_type"] = jacket_type
        jacket_row["jacket_type_key"] = jacket_type["key"]
        jacket_row["jacket_type_label"] = jacket_type["label"]
        jacket_row["detail_key"] = f"{jacket_type['key']}:{jacket_row['object'].tier_enchantment_notation}"
    return jacket_rows


def _get_cache_version():
    cache_version = cache.get(CACHE_VERSION_KEY)
    if cache_version is None:
        cache_version = "initial"
        cache.set(CACHE_VERSION_KEY, cache_version, None)
    return cache_version


def _get_cached_jacket_rows():
    cache_version = _get_cache_version()
    cache_key = CACHED_JACKET_ROWS_KEY.format(version=cache_version)
    jacket_rows = cache.get(cache_key)
    if jacket_rows is None:
        jacket_rows = _build_leather_jacket_rows()
        cache.set(cache_key, jacket_rows, None)
    return jacket_rows


def _get_cached_profitable_rows(
    jacket_rows,
    selected_city_filter,
    selected_jacket_type_filter,
    minimum_percentage_filter,
    minimum_flat_filter,
    selected_sort_by_filter,
    recently_done_keys,
    done_signature,
):
    cache_version = _get_cache_version()
    cache_key = CACHED_PROFITABLE_ROWS_KEY.format(
        version=cache_version,
        city=selected_city_filter,
        jacket_type=selected_jacket_type_filter,
        min_percentage=minimum_percentage_filter,
        min_flat=minimum_flat_filter,
        sort=selected_sort_by_filter,
        done_signature=done_signature,
    )
    profitable_rows = cache.get(cache_key)
    if profitable_rows is None:
        profitable_rows = LeatherJacketProfitabilityService().build_rows(
            jacket_rows,
            selected_city_filter=selected_city_filter,
            selected_jacket_type_filter=selected_jacket_type_filter,
            minimum_percentage=minimum_percentage_filter,
            minimum_flat=minimum_flat_filter,
            sort_by=selected_sort_by_filter,
            recently_done_keys=recently_done_keys,
        )
        cache.set(cache_key, profitable_rows, None)
    return profitable_rows


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
            for jacket_type in LEATHER_JACKET_TYPES:
                jacket_row = rows_by_notation_and_type.get((notation, jacket_type["key"]))
                city_summary = _find_city_summary(jacket_row, city) if jacket_row else None
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


def _build_recently_done_craft_state(jacket_rows, selected_city_filter):
    craft_objects = [jacket_row["object"] for jacket_row in jacket_rows]
    return CraftProfitabilityDoneService().build_recently_done_state(
        craft_objects,
        selected_city_filter,
    )


def _build_city_filter_options():
    return [
        {"value": ALL_CITY_FILTER, "label": "All"},
        *[{"value": city, "label": city_label} for city, city_label in City.choices],
    ]


def _build_jacket_type_filter_options():
    return [
        {"value": ALL_JACKET_TYPE_FILTER, "label": "All"},
        *[
            {"value": jacket_type["key"], "label": jacket_type["label"]}
            for jacket_type in LEATHER_JACKET_TYPES
        ],
    ]


def _find_city_summary(jacket_row, city):
    for city_summary in jacket_row["city_summaries"]:
        if city_summary.city == city:
            return city_summary
    return None


def _sort_notation(notation):
    if notation is None:
        return (0, 0)
    tier, enchantment = notation.split(".")
    return (int(tier), int(enchantment))


def _build_selected_jacket_type_filter(request):
    selected_jacket_type_filter = request.GET.get("jacket_type", ALL_JACKET_TYPE_FILTER)
    if selected_jacket_type_filter == ALL_JACKET_TYPE_FILTER:
        return ALL_JACKET_TYPE_FILTER
    if selected_jacket_type_filter in {jacket_type["key"] for jacket_type in LEATHER_JACKET_TYPES}:
        return selected_jacket_type_filter
    return ALL_JACKET_TYPE_FILTER


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


def _build_query_string(**query_params):
    filtered_query_params = {key: value for key, value in query_params.items() if value not in (None, "")}
    return urlencode(filtered_query_params)


def _queue_price_refresh_job(request, selected_city_filter):
    price_refresh_job = PriceRefreshJob.objects.create(
        kind=PriceRefreshJob.Kind.LEATHER_JACKET,
        context={"city": selected_city_filter},
    )
    refresh_price_job.delay(price_refresh_job_id=price_refresh_job.id)
    messages.success(request, "Le refresh des prix a ete lance en asynchrone.")
    return price_refresh_job


def _build_refresh_job_status_payload(price_refresh_job):
    return {
        "id": price_refresh_job.id,
        "kind": price_refresh_job.kind,
        "status": price_refresh_job.status,
        "refreshed_count": price_refresh_job.refreshed_count,
        "error_message": price_refresh_job.error_message,
        "finished_at": price_refresh_job.finished_at.isoformat() if price_refresh_job.finished_at else None,
    }


def _refresh_prices_and_redirect(request, redirect_url_name, **query_params):
    selected_city_filter = query_params.get("city", DEFAULT_CITY_FILTER)
    price_refresh_job = _queue_price_refresh_job(request, selected_city_filter)
    query_string = _build_query_string(**{**query_params, "refresh_job_id": price_refresh_job.id})
    redirect_url = reverse(redirect_url_name)
    if query_string:
        return redirect(f"{redirect_url}?{query_string}")
    return redirect(redirect_url)


def leather_jacket(request):
    selected_city_filter = _build_selected_city_filter(request)
    if request.method == "POST":
        return _refresh_prices_and_redirect(
            request,
            "albion_online:leather_jacket",
            city=selected_city_filter,
        )

    refresh_job_id = request.GET.get("refresh_job_id")
    refresh_job_id_int = None
    if refresh_job_id:
        try:
            refresh_job_id_int = int(refresh_job_id)
        except ValueError:
            refresh_job_id_int = None
    price_refresh_job = None
    if refresh_job_id_int is not None:
        price_refresh_job = PriceRefreshJob.objects.filter(
            id=refresh_job_id_int,
            kind=PriceRefreshJob.Kind.LEATHER_JACKET,
        ).first()

    jacket_rows = _get_cached_jacket_rows()
    return render(
        request,
        "albion_online/leather_jacket.html",
        {
            "city_filter_options": _build_city_filter_options(),
            "city_tables": _build_city_tables(jacket_rows, selected_city_filter),
            "jacket_types": LEATHER_JACKET_TYPES,
            "selected_city_filter": selected_city_filter,
            "detail_panel_url": reverse("albion_online:leather_jacket_detail_panel"),
            "table_columns_count": len(LEATHER_JACKET_TYPES) + 1,
            "price_refresh_job": price_refresh_job,
            "price_refresh_job_status_url": (
                reverse("albion_online:price_refresh_job_status", kwargs={"job_id": refresh_job_id_int})
                if refresh_job_id_int is not None
                else None
            ),
        },
    )


def leather_jacket_profitability(request):
    selected_city_filter = _build_selected_city_filter(request)
    selected_jacket_type_filter = _build_selected_jacket_type_filter(request)
    minimum_percentage_filter = _build_minimum_percentage_filter(request)
    minimum_flat_filter = _build_minimum_flat_filter(request)
    selected_sort_by_filter = _build_selected_sort_by_filter(request)

    if request.method == "POST":
        return _refresh_prices_and_redirect(
            request,
            "albion_online:leather_jacket_profitability",
            city=selected_city_filter,
            jacket_type=selected_jacket_type_filter,
            min_percentage=minimum_percentage_filter,
            min_flat=minimum_flat_filter,
            sort=selected_sort_by_filter,
        )

    jacket_rows = _get_cached_jacket_rows()
    recently_done_keys, done_signature = _build_recently_done_craft_state(
        jacket_rows,
        selected_city_filter,
    )
    profitable_rows = _get_cached_profitable_rows(
        jacket_rows,
        selected_city_filter,
        selected_jacket_type_filter,
        minimum_percentage_filter,
        minimum_flat_filter,
        selected_sort_by_filter,
        recently_done_keys,
        done_signature,
    )
    return render(
        request,
        "albion_online/leather_jacket_profitability.html",
        {
            "city_filter_options": _build_city_filter_options(),
            "jacket_type_filter_options": _build_jacket_type_filter_options(),
            "minimum_flat_filter": minimum_flat_filter,
            "minimum_percentage_filter": minimum_percentage_filter,
            "refresh_query_string": _build_query_string(
                city=selected_city_filter,
                jacket_type=selected_jacket_type_filter,
                min_percentage=minimum_percentage_filter,
                min_flat=minimum_flat_filter,
                sort=selected_sort_by_filter,
            ),
            "profitable_rows": profitable_rows,
            "detail_panel_url": reverse("albion_online:leather_jacket_detail_panel"),
            "selected_city_filter": selected_city_filter,
            "selected_jacket_type_filter": selected_jacket_type_filter,
            "selected_sort_by_filter": selected_sort_by_filter,
            "sort_by_options": SORT_BY_OPTIONS,
            "profitability_mark_done_url": reverse("albion_online:craft_profitability_mark_done"),
            "profitability_return_url": f"{reverse('albion_online:leather_jacket_profitability')}?{_build_query_string(city=selected_city_filter, jacket_type=selected_jacket_type_filter, min_percentage=minimum_percentage_filter, min_flat=minimum_flat_filter, sort=selected_sort_by_filter)}",
        },
    )


def leather_jacket_detail_panel(request):
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

    jacket_rows = _get_cached_jacket_rows()
    jacket_row = next((row for row in jacket_rows if row["detail_key"] == detail_key), None)
    if jacket_row is None:
        return HttpResponseNotFound("Detail not found.")

    detail_row = MercenaryJacketMarketSummaryService().build_detail_row(jacket_row["object"])
    detail_html = render_to_string(
        "albion_online/leather_jacket_detail_group.html",
        {
            "jacket_row": detail_row,
            "selected_city_filter": selected_city_filter,
        },
        request=request,
    )
    cache.set(cache_key, detail_html, None)
    return HttpResponse(detail_html)


def price_refresh_job_status(request, job_id):
    price_refresh_job = PriceRefreshJob.objects.filter(
        id=job_id,
        kind=PriceRefreshJob.Kind.LEATHER_JACKET,
    ).first()
    if price_refresh_job is None:
        return JsonResponse({"status": "not_found"}, status=404)
    return JsonResponse(_build_refresh_job_status_payload(price_refresh_job))
