from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from django.apps import apps
from django.db.models import Avg, Count, Max, Min, QuerySet

from capitalism.constants.jobs import Job


@dataclass(frozen=True)
class _JobSnapshot:
    alive_count: int = 0
    dead_count: int = 0
    avg_money: float = 0.0
    min_money: float = 0.0
    max_money: float = 0.0
    avg_age: float = 0.0


class HumanAnalyticsRecorderService:
    """Persist per-job analytics for a given simulation day."""

    def __init__(self, *, day_number: int):
        self.day_number = day_number
        self.human_model = apps.get_model("capitalism", "Human")
        self.analytics_model = apps.get_model("capitalism", "HumanAnalytics")

    def run(self) -> None:
        alive_aggregates = self._collect_alive_aggregates()
        dead_counts = self._collect_dead_counts()

        for job_value, _label in Job.choices:
            snapshot = self._build_snapshot(
                job=job_value,
                alive_aggregates=alive_aggregates,
                dead_counts=dead_counts,
            )
            self._store_snapshot(job=job_value, snapshot=snapshot)

    def _collect_alive_aggregates(self) -> Dict[str, Dict[str, float]]:
        queryset: QuerySet = (
            self.human_model.objects.filter(dead=False)
            .values("job")
            .annotate(
                count=Count("id"),
                min_money=Min("money"),
                avg_money=Avg("money"),
                max_money=Max("money"),
                avg_age=Avg("age"),
            )
        )

        aggregates: Dict[str, Dict[str, float]] = {}
        for row in queryset:
            aggregates[row["job"]] = {
                "count": int(row["count"] or 0),
                "min_money": float(row["min_money"] or 0.0),
                "avg_money": float(row["avg_money"] or 0.0),
                "max_money": float(row["max_money"] or 0.0),
                "avg_age": float(row["avg_age"] or 0.0),
            }
        return aggregates

    def _collect_dead_counts(self) -> Dict[str, int]:
        queryset: QuerySet = (
            self.human_model.objects.filter(dead=True)
            .values("job")
            .annotate(count=Count("id"))
        )
        return {row["job"]: int(row["count"] or 0) for row in queryset}

    def _build_snapshot(
        self,
        *,
        job: str,
        alive_aggregates: Dict[str, Dict[str, float]],
        dead_counts: Dict[str, int],
    ) -> _JobSnapshot:
        alive_row = alive_aggregates.get(job)
        dead_count = dead_counts.get(job, 0)
        if not alive_row:
            return _JobSnapshot(dead_count=dead_count)

        return _JobSnapshot(
            alive_count=alive_row["count"],
            dead_count=dead_count,
            avg_money=alive_row["avg_money"],
            min_money=alive_row["min_money"],
            max_money=alive_row["max_money"],
            avg_age=alive_row["avg_age"],
        )

    def _store_snapshot(self, *, job: str, snapshot: _JobSnapshot) -> None:
        self.analytics_model.objects.update_or_create(
            day_number=self.day_number,
            job=job,
            defaults={
                "number_alive": snapshot.alive_count,
                "dead_number": snapshot.dead_count,
                "average_money": snapshot.avg_money,
                "lowest_money": int(snapshot.min_money),
                "max_money": int(snapshot.max_money),
                "average_age": snapshot.avg_age,
                "new_joiner": 0,
            },
        )
