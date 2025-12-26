from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Type

from capitalism.constants import BASE_NEEDS, ObjectType
from capitalism.constants.jobs import Job as JobEnum
from capitalism.services.job_target import JobTargetService
from capitalism.services.jobs import (
    Baker,
    Farmer,
    Lumberjack,
    Miller,
    Miner,
    ToolMaker,
)
from capitalism.services.jobs.base import Job

from .global_price_reference import GlobalPriceReferenceService
from .production_time_cost import time_cost_per_unit


@dataclass(frozen=True)
class _InputSnapshot:
    required_quantity: int
    other_input_cost: float
    time_cost: float


class HumanBuyingPriceValuationService:
    """Estimate the maximum price a human is willing to pay for a given object."""

    HUMAN_JOB_MAPPING = {
        JobEnum.MINER: Miner,
        JobEnum.LUMBERJACK: Lumberjack,
        JobEnum.FARMER: Farmer,
        JobEnum.MILLER: Miller,
        JobEnum.BAKER: Baker,
        JobEnum.TOOLMAKER: ToolMaker,
    }

    CONSUMPTION_NEED_MAP = {object_type: quantity for object_type, quantity in BASE_NEEDS}
    SURVIVAL_EFFECT = 0.2

    def __init__(self):
        self.price_reference = GlobalPriceReferenceService()
        self._reference_prices = self._load_reference_prices()

    def _load_reference_prices(self) -> dict[str, float]:
        return {
            object_type: self.price_reference.get_reference_price(object_type)
            for object_type, _label in ObjectType.choices
        }

    def _reference_price(self, object_type: str) -> float:
        return self._reference_prices.get(
            object_type,
            self.price_reference.get_reference_price(object_type),
        )

    def estimate_price(
        self,
        human,
        object_type: str,
        owned_quantity_override: dict[str, int] | None = None,
    ) -> float:
        job_cls = self._job_class(human)
        if job_cls is None:
            return 0.0

        prices = [
            self._input_purchase_price(human, job_cls, object_type, owned_quantity_override),
            self._consumption_purchase_price(human, object_type, owned_quantity_override),
        ]
        return max(prices)

    def _job_class(self, human) -> Optional[Type[Job]]:
        if human is None:
            return None
        return self.HUMAN_JOB_MAPPING.get(human.job)

    @staticmethod
    def _is_input_for_job(job_cls: Type[Job], object_type: str) -> bool:
        return any(resource_type == object_type for resource_type, _ in job_cls.get_input())

    def _input_purchase_price(
        self,
        human,
        job_cls: Type[Job],
        object_type: str,
        owned_quantity_override: dict[str, int] | None,
    ) -> float:
        if not self._is_input_for_job(job_cls, object_type):
            return 0.0

        if self._has_more_than_two_days_stock(
            human,
            job_cls,
            object_type,
            owned_quantity_override,
        ):
            return 0.0

        snapshot = self._build_input_snapshot(human, job_cls, object_type)
        if snapshot.required_quantity <= 0:
            return 0.0

        theoretical_value = self._theoretical_output_value(job_cls, object_type)
        actionable_budget = max(
            theoretical_value - snapshot.other_input_cost - snapshot.time_cost,
            0.0,
        )
        return actionable_budget / snapshot.required_quantity

    def _consumption_purchase_price(
        self,
        human,
        object_type: str,
        owned_quantity_override: dict[str, int] | None,
    ) -> float:
        if not self._is_consumption_need(object_type):
            return 0.0

        base_value = self._reference_price(object_type)
        survival_effect = self.SURVIVAL_EFFECT * getattr(human, "time_since_need_fulfilled", 0)
        base_value *= 1 + survival_effect
        need_per_day = self.CONSUMPTION_NEED_MAP.get(object_type, 0)
        if need_per_day <= 0:
            return 0.0

        owned_quantity = self._owned_quantity(human, object_type, owned_quantity_override)
        return base_value * (1.0 / (1.0 + owned_quantity / need_per_day))

    def _build_input_snapshot(
        self,
        human,
        job_cls: Type[Job],
        object_type: str,
    ) -> _InputSnapshot:
        other_cost = 0.0
        required_quantity = 0

        for resource_type, qty in job_cls.get_input():
            unit_price = self._reference_price(resource_type)
            if resource_type == object_type:
                required_quantity += qty
            else:
                other_cost += unit_price * qty

        time_cost = time_cost_per_unit(human, job_cls)

        return _InputSnapshot(
            required_quantity=required_quantity,
            other_input_cost=other_cost,
            time_cost=time_cost,
        )

    def _theoretical_output_value(self, job_cls: Type[Job], object_type: str) -> float:
        total = 0.0
        for output_type, qty in job_cls.get_output():
            if output_type == object_type:
                continue
            total += self._output_market_value(output_type, qty)
        return total

    def _output_market_value(self, resource_type: str, qty: int) -> float:
        try:
            unit_price = self._reference_price(resource_type)
        except GlobalPriceReferenceService.PriceNotFound:
            return 0.0
        return unit_price * qty

    def _is_consumption_need(self, object_type: str) -> bool:
        return object_type in self.CONSUMPTION_NEED_MAP

    @staticmethod
    def _has_more_than_two_days_stock(
        human,
        job_cls: Type[Job],
        object_type: str,
        owned_quantity_override: dict[str, int] | None,
    ) -> bool:
        target_quantity = JobTargetService.compute_target_quantity(job_cls, object_type)
        if target_quantity <= 0:
            return False
        owned_quantity = HumanBuyingPriceValuationService._owned_quantity(
            human,
            object_type,
            owned_quantity_override,
        )
        return owned_quantity > target_quantity

    @staticmethod
    def _owned_quantity(
        human,
        object_type: str,
        owned_quantity_override: dict[str, int] | None,
    ) -> int:
        if owned_quantity_override is not None and object_type in owned_quantity_override:
            return owned_quantity_override[object_type]
        return human.get_object_quantity(object_type)
