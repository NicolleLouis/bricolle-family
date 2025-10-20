from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Set

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from habit_tracker.forms.habit_form import HabitUpdateForm
from habit_tracker.models import Habit
from habit_tracker.models.choices import CheckFrequency


@dataclass
class HabitCard:
    habit: Habit
    form: HabitUpdateForm
    success: bool
    checks_last_period: int
    required_checks: int
    streak: int
    period_label: str


def habits_overview(request):
    today = date.today()
    bound_form = None
    bound_habit_id = None

    if request.method == "POST":
        habit_id = request.POST.get("habit_id")
        if not habit_id:
            messages.error(request, "Habitude inconnue.")
            return redirect(reverse("habit_tracker:habits"))
        try:
            habit_instance = Habit.objects.get(pk=habit_id)
        except Habit.DoesNotExist:
            messages.error(request, "Habitude introuvable.")
            return redirect(reverse("habit_tracker:habits"))

        bound_form = HabitUpdateForm(
            request.POST, instance=habit_instance, prefix=str(habit_instance.pk)
        )
        if bound_form.is_valid():
            bound_form.save()
            messages.success(request, "Habitude mise à jour.")
            return redirect(reverse("habit_tracker:habits"))
        bound_habit_id = habit_instance.pk

    habits = list(
        Habit.objects.select_related("objective")
        .prefetch_related("days")
        .order_by("name")
    )

    cards: List[HabitCard] = []
    for habit in habits:
        if bound_form and bound_habit_id == habit.pk:
            bound_form.instance = habit
            form = bound_form
        else:
            form = HabitUpdateForm(instance=habit, prefix=str(habit.pk))

        stats = _compute_habit_stats(habit, today)
        cards.append(
            HabitCard(
                habit=habit,
                form=form,
                success=stats["success"],
                checks_last_period=stats["checks_last_period"],
                required_checks=stats["required_checks"],
                streak=stats["streak"],
                period_label=stats["period_label"],
            )
        )

    return render(
        request,
        "habit_tracker/habits.html",
        {
            "cards": cards,
            "today": today,
        },
    )


def _compute_habit_stats(habit: Habit, today: date) -> dict:
    frequency = habit.check_frequency
    required = 1 if frequency == CheckFrequency.DAILY else habit.objective_in_frequency
    day_dates: Set[date] = {day.date for day in habit.days.all()}

    if frequency == CheckFrequency.DAILY:
        period_start = today - timedelta(days=1)
        period_label = f"Hier ({period_start.strftime('%d/%m/%Y')})"
        success = period_start in day_dates
        checks_last_period = 1 if success else 0
        streak = _compute_daily_streak(day_dates, period_start)
    else:
        current_week_start = today - timedelta(days=today.weekday())
        period_start = current_week_start - timedelta(days=7)
        period_end = period_start + timedelta(days=6)
        period_label = f"Semaine du {period_start.strftime('%d/%m')} au {period_end.strftime('%d/%m')}"
        checks_last_period = _count_weekly_occurrences(day_dates, period_start)
        success = checks_last_period >= required
        streak = _compute_weekly_streak(day_dates, period_start, required)

    return {
        "success": success,
        "checks_last_period": checks_last_period,
        "required_checks": required,
        "streak": streak,
        "period_label": period_label,
    }


def _compute_daily_streak(day_dates: Set[date], start: date) -> int:
    streak = 0
    pointer = start
    while pointer in day_dates:
        streak += 1
        pointer -= timedelta(days=1)
    return streak


def _compute_weekly_streak(day_dates: Set[date], start: date, required: int) -> int:
    streak = 0
    pointer = start
    while _count_weekly_occurrences(day_dates, pointer) >= required:
        streak += 1
        pointer -= timedelta(days=7)
    return streak


def _count_weekly_occurrences(day_dates: Set[date], week_start: date) -> int:
    return sum(
        1 for offset in range(7) if (week_start + timedelta(days=offset)) in day_dates
    )
