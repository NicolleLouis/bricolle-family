from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import redirect, render

from albion_online.constants.city import City
from albion_online.models import Object, Recipe
from albion_online.services.mercenary_jacket_market_summary import (
    MercenaryJacketMarketSummaryService,
)
from albion_online.services.mercenary_jacket_price_refresh import (
    MercenaryJacketPriceRefreshService,
)


def _build_mercenary_jacket_rows():
    mercenary_jackets = (
        Object.objects.filter(
            aodp_id__contains="ARMOR_LEATHER_SET1",
            tier__gte=4,
        )
        .select_related("type")
        .prefetch_related(
            "prices",
            Prefetch(
                "output_recipes",
                queryset=Recipe.objects.prefetch_related("inputs__object__prices"),
            ),
        )
    )
    return MercenaryJacketMarketSummaryService().build_rows(mercenary_jackets)


def leather_jacket(request):
    if request.method == "POST":
        created_prices = MercenaryJacketPriceRefreshService().refresh_prices()
        messages.success(
            request,
            f"{len(created_prices)} price entries refreshed for mercenary jackets.",
        )
        return redirect("albion_online:leather_jacket")

    return render(
        request,
        "albion_online/leather_jacket.html",
        {
            "jacket_rows": _build_mercenary_jacket_rows(),
            "city_headers": City.choices,
            "table_columns_count": len(City.choices) + 1,
        },
    )
