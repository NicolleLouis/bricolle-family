from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Dict, Optional

from django.db import OperationalError, ProgrammingError

from habit_tracker.models import Day, Objective
from habit_tracker.value_objects import ObjectiveProgress


class BaseObjectiveService(ABC):
    TARGET_WINDOW: int = 0
    OBJECTIVE_NAME: str = ""
    PERIOD_LENGTH_DAYS: int = 7

    @classmethod
    def evaluate(cls, today: Optional[date] = None) -> ObjectiveProgress:
        today = today or date.today()

        objective = cls._get_or_create_objective()
        if not objective:
            return cls._empty_progress("Aucune donnée disponible.")

        habit_data = cls._prepare_habits_safe(objective)
        if habit_data is None:
            return cls._empty_progress("Aucune donnée disponible.")

        day_map = cls._build_day_map_safe(today)
        current_period = cls._period_start(today)
        status_period = cls._period_for_status(current_period)
        cache: Dict[date, bool] = {}

        success_count = cls._count_window_successes(current_period, day_map, habit_data, cache)
        streak = cls._compute_streak(current_period, day_map, habit_data, cache)
        status_success = cache.get(status_period, False)
        percentage = cls._calculate_percentage(success_count)
        description = cls._describe_progress(success_count)

        return ObjectiveProgress(
            percentage=percentage,
            completed_value=success_count,
            total_value=cls.TARGET_WINDOW,
            current_streak=streak,
            streak_target=cls.TARGET_WINDOW,
            status_success=status_success,
            progress_description=description,
        )

    # Helpers -----------------------------------------------------------------

    @classmethod
    def _count_window_successes(
        cls,
        current_period: date,
        day_map,
        habit_data,
        cache: Dict[date, bool],
    ) -> int:
        count = 0
        pointer = current_period
        for _ in range(max(cls.TARGET_WINDOW, 0)):
            if cls._period_success(pointer, day_map, habit_data, cache):
                count += 1
            pointer = cls._previous_period_start(pointer)
        return count

    @classmethod
    def _compute_streak(
        cls,
        current_period: date,
        day_map,
        habit_data,
        cache: Dict[date, bool],
    ) -> int:
        streak = 0
        pointer = current_period
        while cls._period_success(pointer, day_map, habit_data, cache):
            streak += 1
            pointer = cls._previous_period_start(pointer)
        return streak

    @classmethod
    def _period_success(
        cls,
        period_start: date,
        day_map,
        habit_data,
        cache: Dict[date, bool],
    ) -> bool:
        if period_start not in cache:
            cache[period_start] = cls._is_period_success(period_start, day_map, habit_data)
        return cache[period_start]

    @classmethod
    def _calculate_percentage(cls, success_count: int) -> float:
        if cls.TARGET_WINDOW <= 0:
            return 0.0
        return round((success_count / cls.TARGET_WINDOW) * 100, 1)

    @classmethod
    def _period_start(cls, reference: date) -> date:
        # Defaults to Monday for weekly periods.
        return reference - timedelta(days=reference.weekday())

    @classmethod
    def _previous_period_start(cls, period_start: date) -> date:
        return period_start - timedelta(days=cls.PERIOD_LENGTH_DAYS)

    @classmethod
    def _period_for_status(cls, current_period: date) -> date:
        """Override if the status (emoji) should represent another period than the current one."""
        return current_period

    @classmethod
    def _describe_progress(cls, success_count: int) -> str:
        if cls.TARGET_WINDOW:
            return f"{success_count} / {cls.TARGET_WINDOW} périodes réussies sur les {cls.TARGET_WINDOW} dernières."
        return "Objectif non configuré."

    @staticmethod
    def _empty_progress(message: str) -> ObjectiveProgress:
        return ObjectiveProgress(percentage=0.0, progress_description=message)

    # Resource management -----------------------------------------------------

    @classmethod
    def _get_or_create_objective(cls) -> Optional[Objective]:
        try:
            objective, _ = Objective.objects.get_or_create(name=cls.OBJECTIVE_NAME)
            return objective
        except (OperationalError, ProgrammingError):
            try:
                objective = Objective(name=cls.OBJECTIVE_NAME)
                objective.save()
                return objective
            except (OperationalError, ProgrammingError):
                return None

    @classmethod
    def _prepare_habits_safe(cls, objective: Objective):
        try:
            return cls._prepare_habits(objective)
        except (OperationalError, ProgrammingError):
            try:
                objective.refresh_from_db()
            except Exception:
                pass
            try:
                return cls._prepare_habits(objective)
            except (OperationalError, ProgrammingError):
                return None

    @classmethod
    def _build_day_map_safe(cls, today: date):
        try:
            days = cls._fetch_days(today)
        except (OperationalError, ProgrammingError):
            return {}
        return cls._build_day_map(days)

    @staticmethod
    def _fetch_days(today: date):
        return Day.objects.filter(date__lte=today).prefetch_related("habits").only("date")

    @staticmethod
    def _build_day_map(days) -> Dict[date, set]:
        mapping: Dict[date, set] = {}
        for day in days:
            mapping[day.date] = set(day.habits.values_list("id", flat=True))
        return mapping

    # Abstract API ------------------------------------------------------------

    @classmethod
    @abstractmethod
    def _prepare_habits(cls, objective: Objective):
        """
        Ensure habits exist for this objective.
        Should return any structure required by `_is_period_success`.
        """

    @classmethod
    @abstractmethod
    def _is_period_success(cls, period_start: date, day_map, habit_data) -> bool:
        """
        Determine if the given period is successful.
        """
