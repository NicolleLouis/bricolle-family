from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING

from capitalism.constants.simulation_step import SimulationStep
from capitalism.services.pricing import HumanSellingPriceValuationService

if TYPE_CHECKING:
    from capitalism.models import Human


class HumanSellingService:
    """Handle the selling phase for a human by resetting and repricing inventory."""

    def __init__(self, human: "Human", valuation_service: HumanSellingPriceValuationService | None = None):
        self.human = human
        self.valuation_service = valuation_service or HumanSellingPriceValuationService()

    def run(self) -> SimulationStep:
        self._reset_listings()
        self._refresh_prices()
        return self._advance_step()

    def _reset_listings(self) -> None:
        self.human.owned_objects.update(price=None, in_sale=False)

    def _refresh_prices(self) -> None:
        owned_types = self.human.owned_objects.values_list("type", flat=True).distinct()
        for object_type in owned_types:
            price = self.valuation_service.estimate_price(self.human, object_type)
            if price is None:
                continue
            formatted_price = self._format_price(price)
            self.human.owned_objects.filter(type=object_type).update(
                price=formatted_price,
                in_sale=True,
            )

    def _advance_step(self) -> SimulationStep:
        return self.human.next_step()

    @staticmethod
    def _format_price(price: float) -> float:
        decimal_price = Decimal(str(price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(decimal_price)
