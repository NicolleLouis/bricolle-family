from django.shortcuts import render
from django.utils import timezone

from agathe.models import PitStop, DiaperChange, VitaminIntake


class HomeController:
    @staticmethod
    def home(request):
        last_pit_stop = PitStop.objects.order_by("-start_date").first()
        last_diaper_change = DiaperChange.objects.order_by("-date").first()
        vitamin_today = VitaminIntake.objects.filter(
            date__date=timezone.now().date()
        ).exists()
        return render(
            request,
            "agathe/home.html",
            {
                "last_pit_stop": last_pit_stop,
                "last_diaper_change": last_diaper_change,
                "vitamin_today": vitamin_today,
            },
        )
