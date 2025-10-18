from datetime import date, timedelta
from typing import Optional, Set

from django.db import OperationalError, ProgrammingError

from habit_tracker.models import Habit, Objective
from habit_tracker.services.base_objective import BaseObjectiveService


class HappinessObjectiveService(BaseObjectiveService):
    TARGET_WINDOW = 31
    OBJECTIVE_NAME = "Être heureux"
    PERIOD_LENGTH_DAYS = 1

    HABITS = (
        "Se coucher avant minuit",
        "Savourer",
        "Méditer",
    )

    @classmethod
    def _prepare_habits(cls, objective: Objective) -> Optional[Set[int]]:
        habit_ids: Set[int] = set()
        for habit_name in cls.HABITS:
            try:
                habit, _ = Habit.objects.get_or_create(
                    name=habit_name,
                    defaults={"objective": objective},
                )
                if habit.objective_id != objective.id:
                    habit.objective = objective
                    habit.save(update_fields=["objective"])
            except (OperationalError, ProgrammingError):
                try:
                    habit = Habit(name=habit_name, objective=objective)
                    habit.save()
                except (OperationalError, ProgrammingError):
                    return None
            habit_ids.add(habit.id)
        return habit_ids

    @classmethod
    def _is_period_success(cls, period_start: date, day_map, habit_ids: Set[int]) -> bool:
        habits = day_map.get(period_start, set())
        return bool(habits and habit_ids.issubset(habits))

    @classmethod
    def _period_start(cls, reference: date) -> date:  # type: ignore[override]
        return reference

    @classmethod
    def _previous_period_start(cls, period_start: date) -> date:  # type: ignore[override]
        return period_start - timedelta(days=1)

    @classmethod
    def _period_for_status(cls, current_period: date) -> date:  # type: ignore[override]
        return current_period - timedelta(days=1)

    @classmethod
    def _describe_progress(cls, success_count: int) -> str:
        if cls.TARGET_WINDOW:
            return (
                f"{success_count} / {cls.TARGET_WINDOW} jours réussis sur les "
                f"{cls.TARGET_WINDOW} derniers."
            )
        return "Objectif non configuré."
