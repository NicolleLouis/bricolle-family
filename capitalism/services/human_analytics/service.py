from __future__ import annotations

from typing import Dict, List

from django.db.models import Avg, Count, Max, Min
from django.apps import apps

from capitalism.constants.jobs import Job


class HumanJobAnalyticsService:
    """Aggregate headcount and monetary statistics per job."""

    def run(self) -> List[Dict[str, object]]:
        aggregates = self._collect_aggregates()
        return self._build_results(aggregates)

    def _collect_aggregates(self) -> Dict[str, Dict[str, object]]:
        Human = self._human_model()
        queryset = (
            Human.objects.values("job")
            .annotate(
                count=Count("id"),
                min_money=Min("money"),
                avg_money=Avg("money"),
                max_money=Max("money"),
            )
        )
        return {row["job"]: row for row in queryset}

    def _build_results(self, aggregates: Dict[str, Dict[str, object]]) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        for job_value, job_label in Job.choices:
            row = aggregates.get(job_value)
            results.append(
                {
                    "job": job_value,
                    "label": job_label,
                    "count": row["count"] if row else 0,
                    "min_money": row["min_money"] if row else None,
                    "avg_money": row["avg_money"] if row else None,
                    "max_money": row["max_money"] if row else None,
                }
            )
        return results

    @staticmethod
    def _human_model():
        return apps.get_model("capitalism", "Human")
