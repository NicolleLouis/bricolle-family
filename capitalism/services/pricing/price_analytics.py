from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from django.apps import apps
from django.db import models
from django.db.models import Avg, Count, Max, Min, QuerySet, Sum

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
        self.object_model = apps.get_model("capitalism", "ObjectStack")
        self.price_analytics_model = apps.get_model("capitalism", "PriceAnalytics")

    def run(self) -> None:
        aggregates = self._collect_price_aggregates()
        existing = {
            analytics.object_type: analytics
            for analytics in self.price_analytics_model.objects.filter(day_number=self.day_number)
        }
        to_create = []
        to_update = []
        for object_type, _label in ObjectType.choices:
            snapshot = aggregates.get(object_type, _PriceSnapshot(0.0, 0.0, 0.0))
            analytics = existing.get(object_type)
            if analytics is None:
                to_create.append(
                    self.price_analytics_model(
                        day_number=self.day_number,
                        object_type=object_type,
                        lowest_price_displayed=snapshot.min_price,
                        max_price_displayed=snapshot.max_price,
                        average_price_displayed=snapshot.avg_price,
                        lowest_price=0.0,
                        max_price=0.0,
                        average_price=0.0,
                        transaction_number=0,
                    )
                )
                continue
            analytics.lowest_price_displayed = snapshot.min_price
            analytics.max_price_displayed = snapshot.max_price
            analytics.average_price_displayed = snapshot.avg_price
            to_update.append(analytics)
        if to_create:
            self.price_analytics_model.objects.bulk_create(to_create, batch_size=200)
        if to_update:
            self.price_analytics_model.objects.bulk_update(
                to_update,
                ["lowest_price_displayed", "max_price_displayed", "average_price_displayed"],
                batch_size=200,
            )

    def _collect_price_aggregates(self) -> Dict[str, _PriceSnapshot]:
        price_expression = models.ExpressionWrapper(
            models.F("price") * models.F("quantity"),
            output_field=models.FloatField(),
        )
        queryset: QuerySet = (
            self.object_model.objects.filter(in_sale=True, price__isnull=False)
            .values("type")
            .annotate(
                min_price=Min("price"),
                max_price=Max("price"),
                total_quantity=Sum("quantity"),
                total_value=Sum(price_expression),
            )
        )

        aggregates: Dict[str, _PriceSnapshot] = {}
        for row in queryset:
            total_quantity = float(row["total_quantity"] or 0.0)
            total_value = float(row["total_value"] or 0.0)
            avg_price = total_value / total_quantity if total_quantity else 0.0
            aggregates[row["type"]] = _PriceSnapshot(
                min_price=float(row["min_price"] or 0.0),
                max_price=float(row["max_price"] or 0.0),
                avg_price=avg_price,
            )
        return aggregates


class TransactionPriceAnalyticsService:
    """Update price analytics with accepted transaction data and clear processed transactions."""

    def __init__(self, *, day_number: int):
        self.day_number = day_number
        self.transaction_model = apps.get_model("capitalism", "Transaction")
        self.price_analytics_model = apps.get_model("capitalism", "PriceAnalytics")

    def run(self) -> None:
        aggregates = self._collect_transaction_aggregates()
        existing = {
            analytics.object_type: analytics
            for analytics in self.price_analytics_model.objects.filter(day_number=self.day_number)
        }
        to_create = []
        to_update = []
        for object_type, _label in ObjectType.choices:
            snapshot = aggregates.get(object_type)
            if snapshot:
                analytics = existing.get(object_type)
                if analytics is None:
                    to_create.append(
                        self.price_analytics_model(
                            day_number=self.day_number,
                            object_type=object_type,
                            lowest_price_displayed=snapshot.min_price,
                            max_price_displayed=snapshot.max_price,
                            average_price_displayed=snapshot.avg_price,
                            lowest_price=snapshot.min_price,
                            max_price=snapshot.max_price,
                            average_price=snapshot.avg_price,
                            transaction_number=snapshot.count,
                        )
                    )
                    continue
                analytics.lowest_price = snapshot.min_price
                analytics.max_price = snapshot.max_price
                analytics.average_price = snapshot.avg_price
                analytics.transaction_number = snapshot.count
                to_update.append(analytics)
            else:
                analytics = existing.get(object_type)
                if analytics is None:
                    to_create.append(
                        self.price_analytics_model(
                            day_number=self.day_number,
                            object_type=object_type,
                            lowest_price_displayed=0.0,
                            max_price_displayed=0.0,
                            average_price_displayed=0.0,
                            lowest_price=0.0,
                            max_price=0.0,
                            average_price=0.0,
                            transaction_number=0,
                        )
                    )
                    continue
                analytics.lowest_price = 0.0
                analytics.max_price = 0.0
                analytics.average_price = 0.0
                analytics.transaction_number = 0
                to_update.append(analytics)
        if to_create:
            self.price_analytics_model.objects.bulk_create(to_create, batch_size=200)
        if to_update:
            self.price_analytics_model.objects.bulk_update(
                to_update,
                ["lowest_price", "max_price", "average_price", "transaction_number"],
                batch_size=200,
            )
        self.transaction_model.objects.all().delete()

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
