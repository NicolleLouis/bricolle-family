from django.apps import apps

from capitalism.constants.object_type import ObjectType

from .global_price_reference import GlobalPriceReferenceService


class MarketPerceivedPriceResetService:
    """Reset perceived prices to the global reference values."""

    def __init__(self, *, day_number: int, price_reference_service: GlobalPriceReferenceService | None = None):
        self._day_number = day_number
        self._price_reference_service = price_reference_service or GlobalPriceReferenceService()

    def reset(self) -> None:
        model = self._model()
        model.objects.all().delete()
        entries = [
            model(
                updated_at=self._day_number,
                object=object_type,
                perceived_price=self._price_reference_service.get_default_price(object_type),
            )
            for object_type, _label in ObjectType.choices
        ]
        model.objects.bulk_create(entries)

    def _model(self):
        return apps.get_model("capitalism", "MarketPerceivedPrice")


class MarketPerceivedPriceUpdateService:
    """Update perceived prices using market analytics for the current day."""

    WEIGHT_CURRENT = 100
    WEIGHT_AVERAGE_PRICE = 10
    WEIGHT_DISPLAYED_AVERAGE = 1

    def __init__(self, *, day_number: int):
        self._day_number = day_number

    def update(self) -> None:
        model = self._market_price_model()
        analytics_map = self._analytics_by_object_type()

        entries = list(model.objects.all())
        to_update = []
        for entry in entries:
            new_price = self._compute_price(entry.perceived_price, analytics_map.get(entry.object))
            if entry.perceived_price != new_price or entry.updated_at != self._day_number:
                entry.perceived_price = new_price
                entry.updated_at = self._day_number
                to_update.append(entry)

        if to_update:
            model.objects.bulk_update(to_update, ["perceived_price", "updated_at"])

    def _market_price_model(self):
        return apps.get_model("capitalism", "MarketPerceivedPrice")

    def _analytics_model(self):
        return apps.get_model("capitalism", "PriceAnalytics")

    def _analytics_by_object_type(self):
        rows = self._analytics_model().objects.filter(day_number=self._day_number)
        return {row.object_type: row for row in rows}

    def _compute_price(self, current_price: float, analytics) -> float:
        current_value = float(current_price)
        weighted_sum = current_value * self.WEIGHT_CURRENT
        total_weight = self.WEIGHT_CURRENT

        if analytics is not None:
            if analytics.transaction_number > 0 and analytics.average_price is not None:
                weighted_sum += float(analytics.average_price) * self.WEIGHT_AVERAGE_PRICE
                total_weight += self.WEIGHT_AVERAGE_PRICE
            avg_displayed = getattr(analytics, "average_price_displayed", None)
            if avg_displayed is not None and avg_displayed != 0:
                weighted_sum += float(avg_displayed) * self.WEIGHT_DISPLAYED_AVERAGE
                total_weight += self.WEIGHT_DISPLAYED_AVERAGE

        return weighted_sum / total_weight if total_weight else current_value
