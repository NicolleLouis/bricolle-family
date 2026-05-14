from django.contrib import messages
from django.http import HttpResponseNotAllowed, HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse

from albion_online.constants.city import City
from albion_online.services.craft_profitability_done import (
    CraftProfitabilityDoneService,
)


def craft_profitability_mark_done(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    object_aodp_id = request.POST.get("object_aodp_id")
    row_city = request.POST.get("row_city")
    return_url = request.POST.get("return_url")
    if not object_aodp_id or row_city not in City.values:
        return HttpResponseNotFound("Missing profitability craft identifiers.")

    if CraftProfitabilityDoneService().mark_done(object_aodp_id, row_city) is None:
        return HttpResponseNotFound("Craft not found.")

    messages.success(request, "Craft marked as done for 12 hours.")
    if return_url and return_url.startswith("/"):
        return redirect(return_url)
    return redirect(reverse("albion_online:home"))
