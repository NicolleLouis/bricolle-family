from datetime import date

from django.db import OperationalError, ProgrammingError
from django.shortcuts import render

from habit_tracker.models import Day, Habit, Objective


def home(request):
    """
    Display a dashboard summary of the habit tracker.
    """
    today = date.today()

    try:
        total_objectives = Objective.objects.count()
        total_habits = Habit.objects.count()
        today_record = (
            Day.objects.filter(date=today)
            .prefetch_related("habits", "habits__objective")
            .first()
        )
        today_habits = list(today_record.habits.all()) if today_record else []

        habits_stats = []
        for habit in Habit.objects.order_by("name"):
            last_date = (
                Day.objects.filter(habits=habit, date__lte=today)
                .order_by("-date")
                .values_list("date", flat=True)
                .first()
            )
            if last_date is not None:
                days_since = (today - last_date).days
            else:
                days_since = None
            habits_stats.append(
                {
                    "habit": habit,
                    "days_since": days_since,
                }
            )
    except (OperationalError, ProgrammingError):
        total_objectives = 0
        total_habits = 0
        today_habits = []
        habits_stats = []

    context = {
        "total_objectives": total_objectives,
        "total_habits": total_habits,
        "today": today,
        "today_habits": today_habits,
        "habits_stats": habits_stats,
    }
    return render(request, "habit_tracker/home.html", context)
