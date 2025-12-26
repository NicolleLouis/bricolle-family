from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING

from django.apps import apps
from django.db import models, transaction

from capitalism.constants.object_type import ObjectType
from capitalism.constants.simulation_step import SimulationStep
from capitalism.services.pricing import HumanBuyingPriceValuationService

if TYPE_CHECKING:
    from capitalism.models import Human


class HumanBuyingService:
    """Handle the buying phase by evaluating market offers against the human budget."""

    def __init__(
        self,
        human: "Human",
        valuation_service: HumanBuyingPriceValuationService | None = None,
    ):
        self.human = human
        self.valuation_service = valuation_service or HumanBuyingPriceValuationService()
        # Resolve models lazily to avoid circular imports during app load.
        self.object_model = apps.get_model("capitalism", "ObjectStack")
        self.transaction_model = apps.get_model("capitalism", "Transaction")

    def run(self) -> SimulationStep:
        self._owned_quantities = self._build_owned_quantities()
        for object_type, _label in ObjectType.choices:
            if self.human.money <= 0:
                break
            self._buy_affordable_objects(object_type)
        return self.human.next_step()

    def _build_owned_quantities(self) -> dict[str, int]:
        rows = (
            self.object_model.objects.filter(owner=self.human)
            .values("type")
            .annotate(total=models.Sum("quantity"))
        )
        return {row["type"]: int(row["total"] or 0) for row in rows}

    def _buy_affordable_objects(self, object_type: str) -> None:
        queryset = (
            self.object_model.objects.select_related("owner")
            .filter(
                type=object_type,
                in_sale=True,
                price__isnull=False,
                price__gt=0,
                quantity__gt=0,
            )
            .exclude(owner=self.human)
            .order_by("price", "id")
        )

        for object_stack in queryset:
            if self.human.money <= 0:
                break
            price = float(object_stack.price or 0)
            if price <= 0:
                continue
            self._process_purchase(object_stack.id, object_type, price)

    def _process_purchase(self, object_id: int, object_type: str, price: float) -> None:
        with transaction.atomic():
            locked_object = (
                self.object_model.objects.select_for_update()
                .select_related("owner")
                .get(id=object_id)
            )
            seller = locked_object.owner
            if seller is None:
                return
            if locked_object.quantity <= 0 or not locked_object.in_sale:
                return
            if locked_object.price is None or float(locked_object.price) != price:
                return

            human_model = apps.get_model("capitalism", "Human")
            buyer = human_model.objects.select_for_update().get(id=self.human.id)
            seller = human_model.objects.select_for_update().get(id=seller.id)

            units_to_buy, buyer_money, seller_money, updated_quantities = self._compute_purchase_units(
                buyer,
                seller,
                object_type,
                price,
                locked_object.quantity,
            )
            if units_to_buy <= 0:
                return

            buyer.money = buyer_money
            buyer.save(update_fields=["money"])
            seller.money = seller_money
            seller.save(update_fields=["money"])

            locked_object.quantity -= units_to_buy
            if locked_object.quantity <= 0:
                locked_object.delete()
            else:
                locked_object.save(update_fields=["quantity"])

            self._add_buyer_stack(buyer, object_type, units_to_buy)
            self._record_transactions(object_type, price, units_to_buy)

            self.human.money = buyer_money
            self._owned_quantities = updated_quantities

    def _compute_purchase_units(
        self,
        buyer: "Human",
        seller: "Human",
        object_type: str,
        price: float,
        available_quantity: int,
    ) -> tuple[int, float, float, dict[str, int]]:
        buyer_money = buyer.money
        seller_money = seller.money
        units_to_buy = 0
        owned_quantities = dict(self._owned_quantities)
        while units_to_buy < available_quantity:
            max_price = self.valuation_service.estimate_price(
                buyer,
                object_type,
                owned_quantity_override=owned_quantities,
            )
            if max_price <= 0 or price > max_price:
                break
            if buyer_money < price:
                break
            buyer_money = self._round_money(buyer_money - price)
            seller_money = self._round_money(seller_money + price)
            units_to_buy += 1
            owned_quantities[object_type] = owned_quantities.get(object_type, 0) + 1
        return units_to_buy, buyer_money, seller_money, owned_quantities

    def _add_buyer_stack(self, buyer: "Human", object_type: str, quantity: int) -> None:
        if quantity <= 0:
            return
        buyer_stack = (
            self.object_model.objects.select_for_update()
            .filter(owner=buyer, type=object_type, in_sale=False, price=None)
            .first()
        )
        if buyer_stack:
            buyer_stack.quantity += quantity
            buyer_stack.save(update_fields=["quantity"])
            return
        self.object_model.objects.create(
            owner=buyer,
            type=object_type,
            quantity=quantity,
            in_sale=False,
            price=None,
        )

    def _record_transactions(self, object_type: str, price: float, quantity: int) -> None:
        if quantity <= 0:
            return
        transactions = [
            self.transaction_model(object_type=object_type, price=price)
            for _ in range(quantity)
        ]
        self.transaction_model.objects.bulk_create(transactions, batch_size=200)

    @staticmethod
    def _round_money(value: float) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
