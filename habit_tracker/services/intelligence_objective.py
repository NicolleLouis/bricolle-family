from datetime import date, timedelta
from typing import Dict, Optional

from django.db import OperationalError, ProgrammingError

from habit_tracker.models import Habit, Objective
from habit_tracker.services.base_objective import BaseObjectiveService


class IntelligenceObjectiveService(BaseObjectiveService):
    TARGET_WINDOW = 20
    OBJECTIVE_NAME = "Être intelligent"
    PERIOD_LENGTH_DAYS = 7

    HABIT_DAILY = "Lire"
    HABIT_ONCE_A_WEEK = ("Réfléchir", "Progresser à un jeux")

    @classmethod
    def _prepare_habits(cls, objective: Objective) -> Optional[Dict[str, int]]:
        habit_map: Dict[str, int] = {}
        for habit_name in (cls.HABIT_DAILY, *cls.HABIT_ONCE_A_WEEK):
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
            habit_map[habit_name] = habit.id
        return habit_map

    @classmethod
    def _is_period_success(cls, period_start: date, day_map, habit_ids: Dict[str, int]) -> bool:
        read_id = habit_ids[cls.HABIT_DAILY]
        once_ids = {habit_ids[name] for name in cls.HABIT_ONCE_A_WEEK}

        read_everyday = True
        once_flags = {habit_id: False for habit_id in once_ids}

        for offset in range(7):
            current_date = period_start + timedelta(days=offset)
            habits = day_map.get(current_date, set())
            if read_id not in habits:
                read_everyday = False
            for habit_id in once_ids:
                if habit_id in habits:
                    once_flags[habit_id] = True

        return read_everyday and all(once_flags.values())

    @classmethod
    def _describe_progress(cls, success_count: int) -> str:
        if cls.TARGET_WINDOW:
            return (
                f"{success_count} / {cls.TARGET_WINDOW} semaines réussies sur les "
                f"{cls.TARGET_WINDOW} dernières."
            )
        return "Objectif non configuré."
