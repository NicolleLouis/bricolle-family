from django.shortcuts import render
from django.utils import timezone
import calendar
from datetime import datetime

from agathe.constants.agathe import AgatheConstant
from agathe.models import PitStop, DiaperChange, VitaminIntake, Bath, AspirinIntake


class HomeController:
    @staticmethod
    def home(request):
        last_pit_stop = PitStop.objects.order_by("-start_date").first()
        last_diaper_change = DiaperChange.objects.order_by("-date").first()
        vitamin_today = VitaminIntake.objects.filter(
            date__date=timezone.now().date()
        ).exists()
        last_bath = Bath.objects.order_by("-date").first()
        last_aspirin = AspirinIntake.objects.order_by("-date").first()
        today = timezone.now().date()
        bath_recent = last_bath and (today - last_bath.date.date()).days <= 2
        aspirin_recent = (
            last_aspirin
            and (timezone.now() - last_aspirin.date).total_seconds() < 8 * 3600
        )
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
                "last_aspirin": last_aspirin,
                "aspirin_recent": aspirin_recent,
                "age_months": months,
                "age_days": days,
            },
        )
