from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List, Optional, Set

from django.db import OperationalError, ProgrammingError
from django.db.models import Prefetch

from habit_tracker.models import Day, Habit, Objective
from habit_tracker.models.choices import CheckFrequency
from habit_tracker.value_objects import ObjectiveProgress


class ObjectiveCompletionService:
    @classmethod
    def evaluate(cls, objective: Objective, *, today: Optional[date] = None) -> ObjectiveProgress:
        today = today or date.today()

        try:
            # Accessing habits may trigger DB operations, so we keep the call inside try/except.
            habits = list(objective.habits.all())
        except (OperationalError, ProgrammingError):
            return cls._empty_progress("Aucune donnée disponible.")

        if not habits:
            return cls._empty_progress("Aucune habitude associée à cet objectif.")

        target_window = max(getattr(objective, "objective_duration", 0) or 0, 0)
        if target_window <= 0:
            return cls._empty_progress("Objectif non configuré.")

        frequency = cls._safe_frequency(objective.check_frequency, CheckFrequency.WEEKLY)
        period_length = cls._period_length_days(frequency)

        reference_date = cls._reference_date(frequency, today)
        current_period = cls._period_start(frequency, reference_date)

        day_map = cls._build_day_map(
            current_period=current_period,
            period_length=period_length,
            window_size=target_window,
        )

        if day_map is None:
            return cls._empty_progress("Aucune donnée disponible.")

        cache: Dict[date, bool] = {}

        success_count = cls._count_window_successes(
            frequency=frequency,
            current_period=current_period,
            habits=habits,
            day_map=day_map,
            cache=cache,
            window_size=target_window,
        )
        streak = cls._compute_streak(
            frequency=frequency,
            current_period=current_period,
            habits=habits,
            day_map=day_map,
            cache=cache,
        )

        status_success = cache.get(current_period, False)
        percentage = round((success_count / target_window) * 100, 1) if target_window else 0.0
        description = cls._describe_progress(success_count, target_window, frequency)

        return ObjectiveProgress(
            percentage=percentage,
            completed_value=success_count,
            total_value=target_window,
            current_streak=streak,
            streak_target=target_window,
            status_success=status_success,
            progress_description=description,
        )

    # Helpers -----------------------------------------------------------------

    @staticmethod
    def _empty_progress(message: str) -> ObjectiveProgress:
        return ObjectiveProgress(percentage=0.0, progress_description=message)

    @staticmethod
    def _period_length_days(frequency: CheckFrequency) -> int:
        return 1 if frequency == CheckFrequency.DAILY else 7

    @classmethod
    def _reference_date(cls, frequency: CheckFrequency, today: date) -> date:
        if frequency == CheckFrequency.DAILY:
            return today - timedelta(days=1)
        return today - timedelta(days=today.weekday() + 1)

    @classmethod
    def _period_start(cls, frequency: CheckFrequency, reference: date) -> date:
        if frequency == CheckFrequency.DAILY:
            return reference
        return reference - timedelta(days=reference.weekday())

    @classmethod
    def _previous_period_start(cls, frequency: CheckFrequency, period_start: date) -> date:
        return period_start - timedelta(days=cls._period_length_days(frequency))

    @classmethod
    def _build_day_map(
        cls,
        *,
        current_period: date,
        period_length: int,
        window_size: int,
    ) -> Optional[Dict[date, Set[int]]]:
        if window_size <= 0:
            return {}

        span_days = period_length * (window_size - 1)
        earliest_period = current_period - timedelta(days=span_days)
        buffer = 6  # capture neighbouring days for weekly checks
        fetch_start = earliest_period - timedelta(days=buffer)
        fetch_end = current_period + timedelta(days=period_length - 1)
        if fetch_start > fetch_end:
            fetch_start = fetch_end

        try:
            day_records = (
                Day.objects.filter(date__range=(fetch_start, fetch_end))
                .prefetch_related(Prefetch("habits", queryset=Habit.objects.only("id")))
                .only("date")
            )
        except (OperationalError, ProgrammingError):
            return None

        mapping: Dict[date, Set[int]] = {}
        for record in day_records:
            mapping[record.date] = set(record.habits.values_list("id", flat=True))
        return mapping

    @classmethod
    def _count_window_successes(
        cls,
        *,
        frequency: CheckFrequency,
        current_period: date,
        habits: List[Habit],
        day_map: Dict[date, Set[int]],
        cache: Dict[date, bool],
        window_size: int,
    ) -> int:
        count = 0
        pointer = current_period
        for _ in range(window_size):
            if cls._period_success(frequency, pointer, habits, day_map, cache):
                count += 1
            pointer = cls._previous_period_start(frequency, pointer)
        return count

    @classmethod
    def _compute_streak(
        cls,
        *,
        frequency: CheckFrequency,
        current_period: date,
        habits: List[Habit],
        day_map: Dict[date, Set[int]],
        cache: Dict[date, bool],
    ) -> int:
        streak = 0
        pointer = current_period
        while cls._period_success(frequency, pointer, habits, day_map, cache):
            streak += 1
            pointer = cls._previous_period_start(frequency, pointer)
        return streak

    @classmethod
    def _period_success(
        cls,
        frequency: CheckFrequency,
        period_start: date,
        habits: List[Habit],
        day_map: Dict[date, Set[int]],
        cache: Dict[date, bool],
    ) -> bool:
        if period_start not in cache:
            cache[period_start] = all(
                cls._habit_success(frequency, habit, period_start, day_map) for habit in habits
            )
        return cache[period_start]

    @classmethod
    def _habit_success(
        cls,
        objective_frequency: CheckFrequency,
        habit: Habit,
        period_start: date,
        day_map: Dict[date, Set[int]],
    ) -> bool:
        habit_frequency = cls._safe_frequency(habit.check_frequency, CheckFrequency.DAILY)
        required_checks = max(habit.objective_in_frequency, 1)
        if objective_frequency == CheckFrequency.DAILY:
            if habit_frequency == CheckFrequency.DAILY:
                return habit.id in day_map.get(period_start, set())
            week_start = period_start - timedelta(days=period_start.weekday())
            week_end = week_start + timedelta(days=6)
            return cls._count_occurrences(habit.id, week_start, week_end, day_map) >= required_checks

        # Objective is weekly
        period_end = period_start + timedelta(days=6)
        if habit_frequency == CheckFrequency.DAILY:
            return cls._daily_habit_fulfilled(habit.id, period_start, period_end, day_map)
        return cls._count_occurrences(habit.id, period_start, period_end, day_map) >= required_checks

    @staticmethod
    def _daily_habit_fulfilled(
        habit_id: int,
        period_start: date,
        period_end: date,
        day_map: Dict[date, Set[int]],
    ) -> bool:
        pointer = period_start
        while pointer <= period_end:
            if habit_id not in day_map.get(pointer, set()):
                return False
            pointer += timedelta(days=1)
        return True

    @staticmethod
    def _count_occurrences(
        habit_id: int,
        start: date,
        end: date,
        day_map: Dict[date, Set[int]],
    ) -> int:
        count = 0
        pointer = start
        while pointer <= end:
            if habit_id in day_map.get(pointer, set()):
                count += 1
            pointer += timedelta(days=1)
        return count

    @staticmethod
    def _safe_frequency(value: Optional[str], default: CheckFrequency) -> CheckFrequency:
        try:
            return CheckFrequency(value) if value is not None else default
        except ValueError:
            return default

    @staticmethod
    def _describe_progress(success_count: int, window_size: int, frequency: CheckFrequency) -> str:
        if window_size <= 0:
            return "Objectif non configuré."
        unit = "jours" if frequency == CheckFrequency.DAILY else "semaines"
        return f"{success_count} / {window_size} {unit} réussis sur les {window_size} derniers."
