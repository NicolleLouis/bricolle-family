from __future__ import annotations

from typing import Dict, List

from django.db.models import Avg, Count, Max, Min

from capitalism.constants.object_type import ObjectType
from capitalism.models.object import Object


class ObjectInventoryStatisticsService:
    """Compute inventory and price statistics for all object types."""

    def run(self) -> List[Dict[str, object]]:
        aggregates = self._collect_aggregates()
        return self._build_results(aggregates)

    def _collect_aggregates(self) -> Dict[str, Dict[str, object]]:
        queryset = (
            Object.objects.values("type")
            .annotate(
                quantity=Count("id"),
                min_price=Min("price"),
                avg_price=Avg("price"),
                max_price=Max("price"),
            )
        )
        return {row["type"]: row for row in queryset}

    def _build_results(self, aggregates: Dict[str, Dict[str, object]]) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        for object_type, label in ObjectType.choices:
            row = aggregates.get(object_type)
            results.append(
                {
                    "type": object_type,
                    "label": label,
                    "quantity": row["quantity"] if row else 0,
                    "min_price": row["min_price"] if row else None,
                    "avg_price": row["avg_price"] if row else None,
                    "max_price": row["max_price"] if row else None,
                }
            )
        return results
