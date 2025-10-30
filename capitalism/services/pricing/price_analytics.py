from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from django.apps import apps
from django.db.models import Avg, Max, Min, QuerySet

from capitalism.constants.object_type import ObjectType


@dataclass(frozen=True)
class _PriceSnapshot:
    min_price: float
    max_price: float
    avg_price: float


class PriceAnalyticsRecorderService:
    """Build or refresh price analytics snapshots for every object type."""

    def __init__(self, *, day_number: int):
        self.day_number = day_number
        self.object_model = apps.get_model("capitalism", "Object")
        self.price_analytics_model = apps.get_model("capitalism", "PriceAnalytics")

    def run(self) -> None:
        aggregates = self._collect_price_aggregates()
        for object_type, _label in ObjectType.choices:
            snapshot = aggregates.get(object_type, _PriceSnapshot(0.0, 0.0, 0.0))
            self._upsert_price_analytics(object_type=object_type, snapshot=snapshot)

    def _collect_price_aggregates(self) -> Dict[str, _PriceSnapshot]:
        queryset: QuerySet = (
            self.object_model.objects.filter(in_sale=True, price__isnull=False)
            .values("type")
            .annotate(
                min_price=Min("price"),
                max_price=Max("price"),
                avg_price=Avg("price"),
            )
        )

        aggregates: Dict[str, _PriceSnapshot] = {}
        for row in queryset:
            aggregates[row["type"]] = _PriceSnapshot(
                min_price=float(row["min_price"] or 0.0),
                max_price=float(row["max_price"] or 0.0),
                avg_price=float(row["avg_price"] or 0.0),
            )
        return aggregates

    def _upsert_price_analytics(self, *, object_type: str, snapshot: _PriceSnapshot) -> None:
        self.price_analytics_model.objects.update_or_create(
            day_number=self.day_number,
            object_type=object_type,
            defaults={
                "lowest_price_displayed": snapshot.min_price,
                "max_price_displayed": snapshot.max_price,
                "average_price_displayed": snapshot.avg_price,
                "lowest_price": snapshot.min_price,
                "max_price": snapshot.max_price,
                "average_price": snapshot.avg_price,
            },
        )
