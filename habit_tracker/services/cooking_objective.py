from datetime import date, timedelta
from typing import Dict, Optional

from django.db import OperationalError, ProgrammingError

from habit_tracker.models import Habit, Objective
from habit_tracker.services.base_objective import BaseObjectiveService


class CookingObjectiveService(BaseObjectiveService):
    TARGET_WINDOW = 20
    OBJECTIVE_NAME = "Être cuisinier"
    PERIOD_LENGTH_DAYS = 7

    HABIT_RECIPES = "Choisir une recette qui fait envie"
    HABIT_COOK = "Cuisiner un plat"

    @classmethod
    def _prepare_habits(cls, objective: Objective) -> Optional[Dict[str, int]]:
        try:
            recipe_habit, _ = Habit.objects.get_or_create(
                name=cls.HABIT_RECIPES,
                defaults={"objective": objective},
            )
            cook_habit, _ = Habit.objects.get_or_create(
                name=cls.HABIT_COOK,
                defaults={"objective": objective},
            )
            cls._ensure_objective_link(recipe_habit, objective)
            cls._ensure_objective_link(cook_habit, objective)
        except (OperationalError, ProgrammingError):
            try:
                recipe_habit = Habit(name=cls.HABIT_RECIPES, objective=objective)
                recipe_habit.save()
                cook_habit = Habit(name=cls.HABIT_COOK, objective=objective)
                cook_habit.save()
            except (OperationalError, ProgrammingError):
                return None

        return {
            "recipe": recipe_habit.id,
            "cook": cook_habit.id,
        }

    @staticmethod
    def _ensure_objective_link(habit: Habit, objective: Objective) -> None:
        if habit.objective_id != objective.id:
            habit.objective = objective
            habit.save(update_fields=["objective"])

    @classmethod
    def _is_period_success(cls, period_start: date, day_map, habit_data: Dict[str, int]) -> bool:
        recipe_id = habit_data["recipe"]
        cook_id = habit_data["cook"]
        recipe_success = True
        cook_count = 0

        for offset in range(7):
            current_date = period_start + timedelta(days=offset)
            habits = day_map.get(current_date, set())
            if recipe_id not in habits:
                recipe_success = False
            if cook_id in habits:
                cook_count += 1

        return recipe_success and cook_count >= 4

    @classmethod
    def _describe_progress(cls, success_count: int) -> str:
        if cls.TARGET_WINDOW:
            return (
                f"{success_count} / {cls.TARGET_WINDOW} semaines réussies sur les "
                f"{cls.TARGET_WINDOW} dernières."
            )
        return "Objectif non configuré."
