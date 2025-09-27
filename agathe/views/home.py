from django.shortcuts import redirect, render
from django.utils import timezone
import calendar
from datetime import datetime

from agathe.constants.agathe import AgatheConstant
from agathe.models import PitStop, DiaperChange, VitaminIntake, Bath
from agathe.forms.pit_stop import PitStopForm


class HomeController:
    @staticmethod
    def home(request):
        if request.method == "POST":
            form = PitStopForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("agathe:home")
        else:
            now = timezone.now()
            form = PitStopForm(
                initial={
                    "start_date": now.strftime("%Y-%m-%dT%H:%M"),
                    "quantity": 90,
                }
            )

        last_pit_stop = PitStop.objects.order_by("-start_date").first()
        last_diaper_change = DiaperChange.objects.order_by("-date").first()
        vitamin_today = VitaminIntake.objects.filter(
            date__date=timezone.now().date()
        ).exists()
        last_bath = Bath.objects.order_by("-date").first()
        today = timezone.now().date()
        bath_recent = last_bath and (today - last_bath.date.date()).days <= 2
        birthdate = datetime.strptime(AgatheConstant.BIRTHDATE, "%Y-%m-%d").date()
        months = (today.year - birthdate.year) * 12 + today.month - birthdate.month
        if today.day < birthdate.day:
            months -= 1
            prev_month = today.month - 1 if today.month > 1 else 12
            prev_year = today.year if today.month > 1 else today.year - 1
            days_in_prev_month = calendar.monthrange(prev_year, prev_month)[1]
            days = today.day + days_in_prev_month - birthdate.day
        else:
            days = today.day - birthdate.day
        return render(
            request,
            "agathe/home.html",
            {
                "last_pit_stop": last_pit_stop,
                "last_diaper_change": last_diaper_change,
                "vitamin_today": vitamin_today,
                "last_bath": last_bath,
                "bath_recent": bath_recent,
                "age_months": months,
                "age_days": days,
                "pit_stop_form": form,
        },
        )
