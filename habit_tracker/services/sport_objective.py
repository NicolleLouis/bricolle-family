from datetime import date, timedelta
from typing import Optional

from django.db import OperationalError, ProgrammingError

from habit_tracker.models import Habit, Objective
from habit_tracker.services.base_objective import BaseObjectiveService


class SportObjectiveService(BaseObjectiveService):
    TARGET_WINDOW = 20
    OBJECTIVE_NAME = "Être sportif"
    PERIOD_LENGTH_DAYS = 7
    HABIT_NAME = "Séance de sport"

    @classmethod
    def _prepare_habits(cls, objective: Objective) -> Optional[int]:
        try:
            habit, created = Habit.objects.get_or_create(
                name=cls.HABIT_NAME,
                defaults={"objective": objective},
            )
            if not created and habit.objective_id != objective.id:
                habit.objective = objective
                habit.save(update_fields=["objective"])
        except (OperationalError, ProgrammingError):
            try:
                habit = Habit(name=cls.HABIT_NAME, objective=objective)
                habit.save()
            except (OperationalError, ProgrammingError):
                return None
        return habit.id

    @classmethod
    def _is_period_success(cls, period_start: date, day_map, habit_id: int) -> bool:
        for offset in range(7):
            current_date = period_start + timedelta(days=offset)
            habits = day_map.get(current_date, set())
            if habit_id in habits:
                return True
        return False

    @classmethod
    def _describe_progress(cls, success_count: int) -> str:
        if cls.TARGET_WINDOW:
            return (
                f"{success_count} / {cls.TARGET_WINDOW} semaines réussies sur les "
                f"{cls.TARGET_WINDOW} dernières."
            )
        return "Objectif non configuré."
