import calendar
from datetime import date

from django.db.models import Prefetch
from django.shortcuts import render

from habit_tracker.models import Habit, Objective
from habit_tracker.services.cooking_objective import CookingObjectiveService
from habit_tracker.services.happiness_objective import HappinessObjectiveService
from habit_tracker.services.intelligence_objective import IntelligenceObjectiveService
from habit_tracker.services.objective_completion import ObjectiveCompletionService
from habit_tracker.services.sport_objective import SportObjectiveService


def objectives_overview(request):
    today = date.today()

    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        first_day = date(year, month, 1)
    except (TypeError, ValueError):
        first_day = date(today.year, today.month, 1)
        year = first_day.year
        month = first_day.month

    last_day = date(year, month, calendar.monthrange(year, month)[1])

    objectives = Objective.objects.prefetch_related(
        Prefetch("habits", queryset=Habit.objects.order_by("name"))
    ).order_by("name")

    objective_cards = []
    for objective in objectives:
        if objective.name == SportObjectiveService.OBJECTIVE_NAME:
            progress_data = SportObjectiveService.evaluate(today)
            total_value = progress_data.total_value or progress_data.streak_target
        elif objective.name == CookingObjectiveService.OBJECTIVE_NAME:
            progress_data = CookingObjectiveService.evaluate(today)
            total_value = progress_data.total_value or progress_data.streak_target
        elif objective.name == HappinessObjectiveService.OBJECTIVE_NAME:
            progress_data = HappinessObjectiveService.evaluate(today)
            total_value = progress_data.total_value or progress_data.streak_target
        elif objective.name == IntelligenceObjectiveService.OBJECTIVE_NAME:
            progress_data = IntelligenceObjectiveService.evaluate(today)
            total_value = progress_data.total_value or progress_data.streak_target
        else:
            progress_data = ObjectiveCompletionService.compute_objective_completion(
                objective,
                start_date=first_day,
                end_date=last_day,
            )
            total_value = progress_data.total_value

        progress = progress_data.percentage
        completed_value = progress_data.completed_value
        current_streak = progress_data.current_streak
        progress_description = progress_data.progress_description or ""
        status_success = progress_data.status_success
        status_label = "Validé" if status_success else "À améliorer"

        objective_cards.append(
            {
                "objective": objective,
                "habits": list(objective.habits.all()),
                "progress": progress,
                "completed_value": completed_value,
                "total_value": total_value,
                "current_streak": current_streak,
                "progress_description": progress_description,
                "status_success": status_success,
                "status_label": status_label,
            }
        )

    context = {
        "objective_cards": objective_cards,
        "today": today,
        "current_month": first_day.strftime("%B %Y"),
        "current_year": year,
        "current_month_number": month,
    }
    return render(request, "habit_tracker/objectives.html", context)
