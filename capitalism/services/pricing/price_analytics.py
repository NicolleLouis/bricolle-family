from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from django.apps import apps
from django.db.models import Avg, Count, Max, Min, QuerySet

from capitalism.constants.object_type import ObjectType


@dataclass(frozen=True)
class _PriceSnapshot:
    min_price: float
    max_price: float
    avg_price: float


@dataclass(frozen=True)
class _TransactionSnapshot:
    min_price: float
    max_price: float
    avg_price: float
    count: int


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
        analytics, created = self.price_analytics_model.objects.get_or_create(
            day_number=self.day_number,
            object_type=object_type,
            defaults={
                "lowest_price_displayed": snapshot.min_price,
                "max_price_displayed": snapshot.max_price,
                "average_price_displayed": snapshot.avg_price,
                "lowest_price": 0.0,
                "max_price": 0.0,
                "average_price": 0.0,
                "transaction_number": 0,
            },
        )

        if not created:
            analytics.lowest_price_displayed = snapshot.min_price
            analytics.max_price_displayed = snapshot.max_price
            analytics.average_price_displayed = snapshot.avg_price
            analytics.save(
                update_fields=[
                    "lowest_price_displayed",
                    "max_price_displayed",
                    "average_price_displayed",
                ]
            )


class TransactionPriceAnalyticsService:
    """Update price analytics with accepted transaction data and clear processed transactions."""

    def __init__(self, *, day_number: int):
        self.day_number = day_number
        self.transaction_model = apps.get_model("capitalism", "Transaction")
        self.price_analytics_model = apps.get_model("capitalism", "PriceAnalytics")

    def run(self) -> None:
        aggregates = self._collect_transaction_aggregates()
        for object_type, snapshot in aggregates.items():
            self._apply_snapshot(object_type=object_type, snapshot=snapshot)
            self.transaction_model.objects.filter(object_type=object_type).delete()

    def _collect_transaction_aggregates(self) -> Dict[str, _TransactionSnapshot]:
        queryset: QuerySet = (
            self.transaction_model.objects.values("object_type")
            .annotate(
                count=Count("id"),
                min_price=Min("price"),
                max_price=Max("price"),
                avg_price=Avg("price"),
            )
        )

        aggregates: Dict[str, _TransactionSnapshot] = {}
        for row in queryset:
            aggregates[row["object_type"]] = _TransactionSnapshot(
                min_price=float(row["min_price"] or 0.0),
                max_price=float(row["max_price"] or 0.0),
                avg_price=float(row["avg_price"] or 0.0),
                count=int(row["count"] or 0),
            )
        return aggregates

    def _apply_snapshot(self, *, object_type: str, snapshot: _TransactionSnapshot) -> None:
        analytics, created = self.price_analytics_model.objects.get_or_create(
            day_number=self.day_number,
            object_type=object_type,
            defaults={
                "lowest_price_displayed": snapshot.min_price,
                "max_price_displayed": snapshot.max_price,
                "average_price_displayed": snapshot.avg_price,
                "lowest_price": snapshot.min_price,
                "max_price": snapshot.max_price,
                "average_price": snapshot.avg_price,
                "transaction_number": snapshot.count,
            },
        )

        if not created:
            analytics.lowest_price = snapshot.min_price
            analytics.max_price = snapshot.max_price
            analytics.average_price = snapshot.avg_price
            analytics.transaction_number = snapshot.count
            analytics.save(
                update_fields=[
                    "lowest_price",
                    "max_price",
                    "average_price",
                    "transaction_number",
                ]
            )
