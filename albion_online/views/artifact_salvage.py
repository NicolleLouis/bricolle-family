from urllib.parse import urlencode

from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from albion_online.constants.city import City
from albion_online.models import PriceRefreshJob
from albion_online.services.artifact_salvage_market_summary import (
    ArtifactSalvageMarketSummaryService,
)
from albion_online.services.price_refresh_cache import ARTIFACT_SALVAGE_CACHE_VERSION_KEY
from albion_online.tasks import refresh_price_job


DEFAULT_CITY_FILTER = City.FORT_STERLING
CACHE_PAYLOAD_VERSION = "v1"
CACHED_SECTIONS_KEY = (
    f"albion_online:artifact_salvage:sections:{{version}}:{CACHE_PAYLOAD_VERSION}:{{city}}"
)


def _build_city_filter_options():
    return [{"value": city, "label": city_label} for city, city_label in City.choices]


def _build_selected_city_filter(request):
    selected_city_filter = request.GET.get("city", DEFAULT_CITY_FILTER)
    if selected_city_filter in City.values:
        return selected_city_filter
    return DEFAULT_CITY_FILTER


def _build_query_string(**query_params):
    filtered_query_params = {key: value for key, value in query_params.items() if value not in (None, "")}
    return urlencode(filtered_query_params)


def _get_cache_version():
    cache_version = cache.get(ARTIFACT_SALVAGE_CACHE_VERSION_KEY)
    if cache_version is None:
        cache_version = "initial"
        cache.set(ARTIFACT_SALVAGE_CACHE_VERSION_KEY, cache_version, None)
    return cache_version


def _build_sections(selected_city_filter):
    return ArtifactSalvageMarketSummaryService().build_sections(selected_city_filter)


def _get_cached_sections(selected_city_filter):
    cache_version = _get_cache_version()
    cache_key = CACHED_SECTIONS_KEY.format(version=cache_version, city=selected_city_filter)
    sections = cache.get(cache_key)
    if sections is None:
        sections = _build_sections(selected_city_filter)
        cache.set(cache_key, sections, None)
    return sections


def _queue_price_refresh_job(request, selected_city_filter):
    price_refresh_job = PriceRefreshJob.objects.create(
        kind=PriceRefreshJob.Kind.ARTIFACT_SALVAGE,
        context={"city": selected_city_filter},
    )
    refresh_price_job.delay(price_refresh_job_id=price_refresh_job.id)
    messages.success(request, "Le refresh des prix a ete lance en asynchrone.")
    return price_refresh_job


def _refresh_prices_and_redirect(request, redirect_url_name, **query_params):
    selected_city_filter = query_params.get("city", DEFAULT_CITY_FILTER)
    price_refresh_job = _queue_price_refresh_job(request, selected_city_filter)
    query_string = _build_query_string(**{**query_params, "refresh_job_id": price_refresh_job.id})
    redirect_url = reverse(redirect_url_name)
    if query_string:
        return redirect(f"{redirect_url}?{query_string}")
    return redirect(redirect_url)


def artifact_salvage(request):
    selected_city_filter = _build_selected_city_filter(request)
    if request.method == "POST":
        return _refresh_prices_and_redirect(
            request,
            "albion_online:artifact_salvage",
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
            kind=PriceRefreshJob.Kind.ARTIFACT_SALVAGE,
        ).first()

    sections = _get_cached_sections(selected_city_filter)
    return render(
        request,
        "albion_online/artifact_salvage.html",
        {
            "city_filter_options": _build_city_filter_options(),
            "price_refresh_job": price_refresh_job,
            "price_refresh_job_status_url": (
                reverse("albion_online:price_refresh_job_status", kwargs={"job_id": refresh_job_id_int})
                if refresh_job_id_int is not None
                else None
            ),
            "selected_city_filter": selected_city_filter,
            "sections": sections,
        },
    )
