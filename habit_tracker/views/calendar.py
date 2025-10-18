import calendar
from datetime import date, timedelta

from django.db import OperationalError, ProgrammingError
from django.shortcuts import render

from habit_tracker.models import Day


def calendar_view(request):
    today = date.today()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        target = date(year, month, 1)
    except (TypeError, ValueError):
        target = date(today.year, today.month, 1)
        year = target.year
        month = target.month
    month_calendar = calendar.Calendar(firstweekday=0)
    month_days = month_calendar.monthdatescalendar(year, month)

    start_range = month_days[0][0]
    end_range = month_days[-1][-1]
    day_records = Day.objects.filter(date__range=(start_range, end_range)).prefetch_related("habits")
    day_lookup = {record.date: record.habits.count() for record in day_records}

    weeks = []
    for week in month_days:
        week_data = []
        for day_obj in week:
            week_data.append(
                {
                    "date": day_obj,
                    "in_current_month": day_obj.month == month,
                    "habit_count": day_lookup.get(day_obj, 0),
                }
            )
        weeks.append(week_data)

    prev_month = (target.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month = (target.replace(day=28) + timedelta(days=4)).replace(day=1)

    context = {
        "weeks": weeks,
        "current_month": target.strftime("%B %Y"),
        "current_year": year,
        "current_month_number": month,
        "prev_year": prev_month.year,
        "prev_month": prev_month.month,
        "next_year": next_month.year,
        "next_month": next_month.month,
        "today": today,
        "weekdays": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
    }
    return render(request, "habit_tracker/calendar.html", context)
