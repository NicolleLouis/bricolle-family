from datetime import timedelta

from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from babyberon.models import Contraction
from babyberon.services.contraction_stats_chart import ContractionStatsChartService


class ContractionController:
    @staticmethod
    def page(request):
        since = timezone.now() - timedelta(hours=2)
        contractions = Contraction.objects.filter(created_at__gte=since).order_by('-created_at')
        count = contractions.count()
        return render(
            request,
            "babyberon/contraction.html",
            {"contractions": contractions, "contraction_count": count},
        )

    @staticmethod
    def stats(request):
        chart_div = ContractionStatsChartService.generate()
        return render(
            request,
            "babyberon/contraction_stats.html",
            {"chart_div": chart_div},
        )

    @staticmethod
    @require_POST
    def add(request, power: int):
        power = max(1, min(3, int(power)))
        Contraction.objects.create(power=power)
        return JsonResponse({"status": "ok"})
