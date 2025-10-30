from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING, Iterable, List

from capitalism.constants.simulation_step import SimulationStep
from capitalism.services.pricing import HumanSellingPriceValuationService

if TYPE_CHECKING:
    from capitalism.models import Human, Object


class HumanSellingService:
    """Handle the selling phase for a human by resetting and repricing inventory."""

    def __init__(self, human: "Human", valuation_service: HumanSellingPriceValuationService | None = None):
        self.human = human
        self.valuation_service = valuation_service or HumanSellingPriceValuationService()

    def run(self) -> SimulationStep:
        objects = list(self._owned_objects())
        self._reset_listings(objects)
        self._refresh_prices(objects)
        return self._advance_step()

    def _owned_objects(self) -> Iterable["Object"]:
        return self.human.owned_objects.all()

    def _reset_listings(self, objects: List["Object"]) -> None:
        for obj in objects:
            obj.price = 0
            obj.in_sale = False
            obj.save(update_fields=["price", "in_sale"])

    def _refresh_prices(self, objects: List["Object"]) -> None:
        for obj in objects:
            price = self.valuation_service.estimate_price(self.human, obj.type)
            if price is None:
                continue
            obj.price = self._format_price(price)
            obj.in_sale = True
            obj.save(update_fields=["price", "in_sale"])

    def _advance_step(self) -> SimulationStep:
        return self.human.next_step()

    @staticmethod
    def _format_price(price: float) -> float:
        decimal_price = Decimal(str(price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(decimal_price)
