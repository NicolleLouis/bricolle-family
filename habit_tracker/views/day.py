from datetime import date, datetime

from django.contrib import messages
from django.db import OperationalError, ProgrammingError
from django.shortcuts import redirect, render
from django.urls import reverse

from habit_tracker.forms.day_form import DayForm
from habit_tracker.models import Day, Habit


def day_create(request):
    today = date.today()
    date_param = request.GET.get("date")

    try:
        target_date = datetime.strptime(date_param, "%Y-%m-%d").date() if date_param else today
    except (TypeError, ValueError):
        target_date = today

    try:
        Habit.objects.count()
        Day.objects.count()
    except (OperationalError, ProgrammingError):
        messages.error(
            request,
            "Les tables nécessaires ne sont pas encore disponibles. Appliquez les migrations avant d'enregistrer une journée.",
        )
        return redirect("habit_tracker:calendar")

    if request.method == "POST":
        form = DayForm(request.POST)
        if form.is_valid():
            day = form.save()
            messages.success(request, "La journée a été enregistrée avec succès.")
            return redirect(f"{reverse('habit_tracker:calendar')}?year={day.date.year}&month={day.date.month}")
    else:
        initial = {"date": target_date}
        existing_day = Day.objects.filter(date=target_date).prefetch_related("habits").first()
        if existing_day:
            initial["habits"] = existing_day.habits.all()
        form = DayForm(initial=initial)

    return render(
        request,
        "habit_tracker/day_form.html",
        {
            "form": form,
            "target_date": target_date,
        },
    )
