from django.shortcuts import render

from agathe.models import PitStop, DiaperChange


class HomeController:
    @staticmethod
    def home(request):
        last_pit_stop = PitStop.objects.order_by("-start_date").first()
        last_diaper_change = DiaperChange.objects.order_by("-date").first()
        return render(
            request,
            "agathe/home.html",
            {
                "last_pit_stop": last_pit_stop,
                "last_diaper_change": last_diaper_change,
            },
        )
