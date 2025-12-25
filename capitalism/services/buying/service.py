from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import logging
from typing import TYPE_CHECKING

from django.apps import apps
from django.db import models, transaction

from capitalism.constants.object_type import ObjectType
from capitalism.constants.simulation_step import SimulationStep
from capitalism.services.pricing import HumanBuyingPriceValuationService

if TYPE_CHECKING:
    from capitalism.models import Human, Object

logger = logging.getLogger(__name__)


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
        self.object_model = apps.get_model("capitalism", "Object")
        self.transaction_model = apps.get_model("capitalism", "Transaction")

    def run(self) -> SimulationStep:
        for object_type, _label in ObjectType.choices:
            if self.human.money <= 0:
                break
            self._buy_affordable_objects(object_type)
        return self.human.next_step()

    def _buy_affordable_objects(self, object_type: str) -> None:
        queryset = (
            self.object_model.objects.select_related("owner")
            .filter(
                type=object_type,
                in_sale=True,
                price__isnull=False,
                price__gt=0,
            )
            .exclude(owner=self.human)
            .order_by("price", "id")
        )

        for obj in queryset:
            max_price = self.valuation_service.estimate_price(self.human, object_type)
            if max_price <= 0:
                break

            price = float(obj.price or 0)
            if price > max_price:
                break
            if self.human.money < price:
                break
            self._process_purchase(obj, price)

    def _process_purchase(self, obj: "Object", price: float) -> None:
        seller = obj.owner
        if seller is None:
            return

        with transaction.atomic():
            total_before = self._total_money()
            self._debit_buyer(price)
            self._credit_seller(seller, price)
            self._transfer_object(obj)
            self._record_transaction(obj.type, price)
            total_after = self._total_money()
            logger.info(
                "Transaction: object=%s price=%.2f buyer_id=%s buyer_job=%s seller_id=%s seller_job=%s total_before=%.2f total_after=%.2f",
                obj.type,
                price,
                self.human.id,
                self.human.job,
                seller.id,
                seller.job,
                total_before,
                total_after,
            )

    def _debit_buyer(self, amount: float) -> None:
        raw_value = self.human.money - amount
        rounded_value = self._round_money(raw_value)
        if rounded_value != raw_value:
            logger.info(
                "Money rounding (buyer): human_id=%s raw=%s rounded=%s amount=%s",
                self.human.id,
                raw_value,
                rounded_value,
                amount,
            )
        self.human.money = rounded_value
        self.human.save(update_fields=["money"])

    @staticmethod
    def _credit_seller(seller: "Human", amount: float) -> None:
        seller.refresh_from_db(fields=["money"])
        raw_value = seller.money + amount
        rounded_value = HumanBuyingService._round_money(raw_value)
        if rounded_value != raw_value:
            logger.info(
                "Money rounding (seller): human_id=%s raw=%s rounded=%s amount=%s",
                seller.id,
                raw_value,
                rounded_value,
                amount,
            )
        seller.money = rounded_value
        seller.save(update_fields=["money"])

    def _transfer_object(self, obj: "Object") -> None:
        obj.owner = self.human
        obj.in_sale = False
        obj.price = None
        obj.save(update_fields=["owner", "in_sale", "price"])

    def _record_transaction(self, object_type: str, price: float) -> None:
        self.transaction_model.objects.create(object_type=object_type, price=price)

    @staticmethod
    def _round_money(value: float) -> float:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def _total_money() -> float:
        human_model = apps.get_model("capitalism", "Human")
        total = human_model.objects.aggregate(total=models.Sum("money"))["total"]
        return float(total or 0.0)
