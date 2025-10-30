from __future__ import annotations

from typing import Optional, Type

from capitalism.constants import BASE_NEEDS
from capitalism.constants.jobs import Job as JobEnum
from capitalism.constants.object_type import ObjectType
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

    def __init__(self):
        self.price_reference = GlobalPriceReferenceService()

    def estimate_price(self, human, object_type: str) -> float:
        job_cls = self._human_job_class(human)
        if job_cls is None:
            return 0.0

        base_price = 0.0
        if self._is_input_for_job(job_cls, object_type):
            if not self._has_more_than_two_days_stock(human, job_cls, object_type):
                base_price = max(base_price, self._input_driven_price(human, job_cls, object_type))

        if self._is_consumption_need(object_type):
            base_price = max(base_price, self._consumption_price(human, object_type))

        return base_price

    def _human_job_class(self, human) -> Optional[Type[Job]]:
        if human is None:
            return None
        return self.HUMAN_JOB_MAPPING.get(human.job)

    def _is_input_for_job(self, job_cls: Type[Job], object_type: str) -> bool:
        return any(resource_type == object_type for resource_type, _ in job_cls.get_input())

    def _input_driven_price(self, human, job_cls: Type[Job], object_type: str) -> float:
        total_input_cost = 0.0
        input_quantity = 0
        for resource_type, qty in job_cls.get_input():
            unit_price = self.price_reference.get_reference_price(resource_type)
            total_input_cost += unit_price * qty
            if resource_type == object_type:
                input_quantity += qty

        if input_quantity <= 0:
            return 0.0

        return self._allocate_cost_to_output(
            job_cls,
            object_type,
            total_input_cost,
            input_quantity,
        )

    def _is_consumption_need(self, object_type: str) -> bool:
        return object_type in self.CONSUMPTION_NEED_MAP

    def _consumption_price(self, human, object_type: str) -> float:
        base_value = self.price_reference.get_reference_price(object_type)
        need_per_day = self.CONSUMPTION_NEED_MAP.get(object_type, 0)
        if need_per_day <= 0:
            return 0.0

        owned_quantity = human.owned_objects.filter(type=object_type).count()
        return base_value * (1.0 / (1.0 + (owned_quantity / need_per_day)))

    def _allocate_cost_to_output(
        self,
        job_cls: Type[Job],
        object_type: str,
        total_input_cost: float,
        input_quantity: int,
    ) -> float:
        outputs = list(job_cls.get_output())
        multiple_outputs = len(outputs) > 1
        competing_output_value = 0.0

        if multiple_outputs:
            for resource_type, qty in outputs:
                if resource_type != object_type:
                    competing_output_value += self._output_market_value(resource_type, qty)

        actionable_cost = max(total_input_cost - competing_output_value, 0.0)
        return actionable_cost / input_quantity

    def _output_market_value(self, resource_type: str, qty: int) -> float:
        try:
            unit_price = self.price_reference.get_reference_price(resource_type)
        except GlobalPriceReferenceService.PriceNotFound:
            return 0.0
        return unit_price * qty

    def _has_more_than_two_days_stock(self, human, job_cls: Type[Job], object_type: str) -> bool:
        target_quantity = JobTargetService.compute_target_quantity(job_cls, object_type)
        if target_quantity <= 0:
            return False
        owned_quantity = human.owned_objects.filter(type=object_type).count()
        return owned_quantity > target_quantity
