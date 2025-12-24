from django.shortcuts import redirect, render

from runeterra.services.monthly_challenge import (
    MonthlyChallengeAvailableService,
    MonthlyChallengeConsumeService,
    MonthlyChallengeResetService,
)


def monthly_challenge(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "reset":
            MonthlyChallengeResetService().reset()
        elif action == "consume":
            champion_id = request.POST.get("champion_id")
            try:
                MonthlyChallengeConsumeService().consume(int(champion_id))
            except (TypeError, ValueError):
                pass
        return redirect("runeterra:monthly_challenge")

    star_level = request.GET.get("star_level")
    selected_star_level = None
    if star_level:
        try:
            selected_star_level = int(star_level)
        except (TypeError, ValueError):
            selected_star_level = None

    available_service = MonthlyChallengeAvailableService()
    champions, star_counts, total_available = available_service.list_available()
    if selected_star_level is None:
        for star in range(2, 8):
            if star_counts.get(star, 0) > 0:
                selected_star_level = star
                break
    if selected_star_level is not None:
        champions, _, _ = available_service.list_available(selected_star_level)
    spotlight = available_service.pick_spotlight()
    star_filters = [
        {"star": star, "count": star_counts[star]} for star in range(2, 8)
    ]
    return render(
        request,
        "runeterra/monthly_challenge.html",
        {
            "champions": champions,
            "star_filters": star_filters,
            "selected_star_level": selected_star_level,
            "total_available": total_available,
            "spotlight": spotlight,
        },
    )
