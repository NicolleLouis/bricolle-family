from datetime import date, timedelta
from typing import Dict, Iterable, Sequence

from django.db import OperationalError, ProgrammingError
from django.db.models import Prefetch

from habit_tracker.models import Day, Habit, Objective
from habit_tracker.value_objects import ObjectiveProgress


class ObjectiveCompletionService:
    OBJECTIVE_NAMES: Iterable[str] = (
        "Être sportif",
        "Être cuisinier",
        "Être heureux",
        "Être intelligent",
    )

    @classmethod
    def ensure_objectives(cls) -> Dict[str, Objective]:
        """
        Ensure required objectives exist and return them keyed by name.
        Gracefully handle missing tables (e.g. before migrations) by returning an empty mapping.
        """
        objectives: Dict[str, Objective] = {}
        try:
            for name in cls.OBJECTIVE_NAMES:
                objective, _ = Objective.objects.get_or_create(name=name)
                objectives[name] = objective
        except (OperationalError, ProgrammingError):
            return {}
        return objectives

    @staticmethod
    def _generate_dates(start_date: date, end_date: date) -> Sequence[date]:
        delta = end_date - start_date
        return [start_date + timedelta(days=i) for i in range(delta.days + 1)]

    @classmethod
    def compute_objective_completion(
        cls,
        objective: Objective,
        *,
        start_date: date,
        end_date: date,
    ) -> ObjectiveProgress:
        """
        Compute completion ratio for an objective between two dates (inclusive).
        Returns zero progress if prerequisite tables are missing.
        """
        try:
            cls.ensure_objectives()
        except (OperationalError, ProgrammingError):
            return ObjectiveProgress(percentage=0.0, progress_description="Aucune donnée disponible.")

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        days_in_period = cls._generate_dates(start_date, end_date)
        total_days = len(days_in_period)

        habits = objective.habits.all()
        habit_ids = set(habits.values_list("id", flat=True))

        if total_days == 0 or not habit_ids:
            return ObjectiveProgress(
                percentage=0.0,
                completed_value=0,
                total_value=total_days,
                progress_description="Aucune donnée sur la période sélectionnée.",
            )

        try:
            day_records = (
                Day.objects.filter(date__range=(start_date, end_date))
                .prefetch_related(Prefetch("habits", queryset=Habit.objects.only("id")))
        )
        except (OperationalError, ProgrammingError):
            return ObjectiveProgress(
                percentage=0.0,
                completed_value=0,
                total_value=total_days,
                progress_description="Aucune donnée sur la période sélectionnée.",
            )

        day_lookup = {record.date: set(record.habits.values_list("id", flat=True)) for record in day_records}

        completed_days = sum(1 for day in days_in_period if habit_ids.issubset(day_lookup.get(day, set())))
        percentage = round((completed_days / total_days) * 100, 1) if total_days else 0.0

        status_success = percentage >= 70.0 if total_days else False
        description = (
            f"{completed_days} / {total_days} jours validés ce mois-ci."
            if total_days
            else "Aucune donnée sur la période sélectionnée."
        )

        return ObjectiveProgress(
            percentage=percentage,
            completed_value=completed_days,
            total_value=total_days,
            status_success=status_success,
            progress_description=description,
        )
