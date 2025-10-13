import calendar
from datetime import date

from django.shortcuts import render
from django.utils import timezone

from sport.models import Session


def _month_start_from_request(request):
    today = timezone.now().date()
    year = request.GET.get("year")
    month = request.GET.get("month")
    try:
        if year is not None and month is not None:
            year = int(year)
            month = int(month)
            return date(year, month, 1)
    except (TypeError, ValueError):
        pass
    return today.replace(day=1)


def _shift_month(month_start, offset):
    new_month = month_start.month - 1 + offset
    year = month_start.year + new_month // 12
    month = new_month % 12 + 1
    return date(year, month, 1)


def home(request):
    month_start = _month_start_from_request(request)
    cal = calendar.Calendar(firstweekday=0)
    month_weeks = cal.monthdatescalendar(month_start.year, month_start.month)
    calendar_start = month_weeks[0][0]
    calendar_end = month_weeks[-1][-1]

    sessions = (
        Session.objects.select_related("training")
        .filter(date__gte=calendar_start, date__lte=calendar_end)
        .order_by("date")
    )
    sessions_by_day = {}
    for session in sessions:
        sessions_by_day.setdefault(session.date, []).append(session)

    weeks = []
    for week in month_weeks:
        week_data = []
        for day in week:
            week_data.append(
                {
                    "date": day,
                    "in_month": day.month == month_start.month,
                    "sessions": sessions_by_day.get(day, []),
                }
            )
        weeks.append(week_data)

    today = timezone.now().date()
    recent_sessions = (
        Session.objects.select_related("training")
        .filter(date__lt=today)
        .order_by("-date")[:5]
    )
    upcoming_sessions = (
        Session.objects.select_related("training")
        .filter(date__gte=today)
        .order_by("date")[:5]
    )

    context = {
        "weeks": weeks,
        "month_label": month_start.strftime("%B %Y"),
        "current_month": month_start,
        "prev_month": _shift_month(month_start, -1),
        "next_month": _shift_month(month_start, 1),
        "today": today,
        "recent_sessions": recent_sessions,
        "upcoming_sessions": upcoming_sessions,
    }
    return render(request, "sport/home.html", context)
