from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING

from capitalism.constants import BASE_NEEDS
from capitalism.constants.simulation_step import SimulationStep
from capitalism.services.pricing import HumanSellingPriceValuationService

if TYPE_CHECKING:
    from capitalism.models import Human


class HumanSellingService:
    """Handle the selling phase for a human by resetting and repricing inventory."""

    SELLABLE_SURPLUS_RATIO = 0.5

    def __init__(self, human: "Human", valuation_service: HumanSellingPriceValuationService | None = None):
        self.human = human
        self.valuation_service = valuation_service or HumanSellingPriceValuationService()
        self._base_need_quantities = {object_type: quantity for object_type, quantity in BASE_NEEDS}

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
            total_quantity = self.human.get_object_quantity(object_type)
            sale_quantity = self._sale_quantity_for_type(object_type, total_quantity)
            if sale_quantity <= 0:
                continue
            formatted_price = self._format_price(price)
            self._list_objects_for_sale(object_type, formatted_price, sale_quantity)

    def _sale_quantity_for_type(self, object_type: str, total_quantity: int) -> int:
        if total_quantity <= 0:
            return 0
        base_reserve = self._base_need_quantities.get(object_type, 0)
        if total_quantity <= base_reserve:
            return 0
        sellable_quantity = total_quantity - base_reserve
        sale_quantity = int(sellable_quantity * self.SELLABLE_SURPLUS_RATIO)
        if sale_quantity == 0 and sellable_quantity > 0:
            sale_quantity = 1
        keep_at_least = base_reserve if base_reserve > 0 else min(1, total_quantity)
        max_sale = max(0, total_quantity - keep_at_least)
        return min(sale_quantity, max_sale)

    def _list_objects_for_sale(self, object_type: str, price: float, quantity: int) -> None:
        if quantity <= 0:
            return
        remaining = quantity
        object_stack_model = self.human.owned_objects.model
        stacks = self.human.owned_objects.filter(type=object_type, in_sale=False).order_by("id")
        for stack in stacks:
            if remaining <= 0:
                break
            if stack.quantity <= remaining:
                stack.in_sale = True
                stack.price = price
                stack.save(update_fields=["in_sale", "price"])
                remaining -= stack.quantity
                continue
            stack.quantity -= remaining
            stack.save(update_fields=["quantity"])
            object_stack_model.objects.create(
                owner=self.human,
                type=object_type,
                quantity=remaining,
                in_sale=True,
                price=price,
            )
            remaining = 0

    def _advance_step(self) -> SimulationStep:
        return self.human.next_step()

    @staticmethod
    def _format_price(price: float) -> float:
        decimal_price = Decimal(str(price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(decimal_price)
