from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate

from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from babyberon.models import Contraction


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
        today = timezone.now().date()
        since = today - timedelta(days=6)

        queryset = (
            Contraction.objects.filter(created_at__date__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .order_by("day")
            .annotate(count=Count("id"))
        )
        counts_by_day = {item["day"]: item["count"] for item in queryset}

        labels = []
        counts = []
        for i in range((today - since).days + 1):
            day = since + timedelta(days=i)
            labels.append(day.strftime("%d/%m"))
            counts.append(counts_by_day.get(day, 0))

        return render(
            request,
            "babyberon/contraction_stats.html",
            {"labels": labels, "counts": counts},
        )

    @staticmethod
    @require_POST
    def add(request, power: int):
        power = max(1, min(3, int(power)))
        Contraction.objects.create(power=power)
        return JsonResponse({"status": "ok"})
