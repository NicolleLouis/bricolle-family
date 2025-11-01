from __future__ import annotations

from typing import Dict, List

from django.db.models import Count

from capitalism.constants.object_type import ObjectType
from capitalism.models import MarketPerceivedPrice
from capitalism.models.object import Object


class ObjectInventoryStatisticsService:
    """Compute inventory and price statistics for all object types."""

    def run(self) -> List[Dict[str, object]]:
        aggregates = self._collect_aggregates()
        return self._build_results(aggregates)

    def _collect_aggregates(self) -> Dict[str, Dict[str, object]]:
        queryset = Object.objects.values("type").annotate(quantity=Count("id"))
        return {row["type"]: row for row in queryset}

    def _build_results(self, aggregates: Dict[str, Dict[str, object]]) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        perceived_map = {
            entry.object: entry.perceived_price for entry in MarketPerceivedPrice.objects.all()
        }
        for object_type, label in ObjectType.choices:
            row = aggregates.get(object_type)
            results.append(
                {
                    "type": object_type,
                    "label": label,
                    "quantity": row["quantity"] if row else 0,
                    "perceived_price": perceived_map.get(object_type),
                }
            )
        return results
