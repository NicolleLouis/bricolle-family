from __future__ import annotations

from typing import Dict, List

from django.db.models import Sum

from capitalism.constants.object_type import ObjectType
from capitalism.models import MarketPerceivedPrice
from capitalism.models.object_stack import ObjectStack


class ObjectInventoryStatisticsService:
    """Compute inventory and price statistics for all object types."""

    def run(self) -> List[Dict[str, object]]:
        aggregates = self._collect_aggregates()
        return self._build_results(aggregates)

    def _collect_aggregates(self) -> Dict[str, Dict[str, object]]:
        queryset = ObjectStack.objects.values("type").annotate(quantity=Sum("quantity"))
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
                    "quantity": int(row["quantity"] or 0) if row else 0,
                    "perceived_price": perceived_map.get(object_type),
                }
            )
        return results
