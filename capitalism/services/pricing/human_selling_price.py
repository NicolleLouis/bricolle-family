from __future__ import annotations

from typing import Optional, Type

from capitalism.constants.jobs import Job as JobEnum
from capitalism.services.job_capacity import JobCapacityService
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


class HumanSellingPriceValuationService:
    """Estimate the selling price a human is willing to ask for a produced object."""

    MARKUP_BASE = 0.2
    STOCK_EFFECT= 0.2
    HUMAN_JOB_MAPPING = {
        JobEnum.MINER: Miner,
        JobEnum.LUMBERJACK: Lumberjack,
        JobEnum.FARMER: Farmer,
        JobEnum.MILLER: Miller,
        JobEnum.BAKER: Baker,
        JobEnum.TOOLMAKER: ToolMaker,
    }

    def __init__(self):
        self.price_reference = GlobalPriceReferenceService()

    def estimate_price(self, human, object_type: str) -> Optional[float]:
        job_cls = self._human_job_class(human)
        if job_cls is None:
            return None

        if not self._human_produces_object(job_cls, object_type):
            return None

        unit_cost = self._compute_unit_cost(human, job_cls)
        markup = self.MARKUP_BASE
        stock_effect = self._stock_effect(human, job_cls, object_type)
        raw_price = unit_cost * (1 + markup - stock_effect)
        return max(0.01, raw_price)

    def _human_job_class(self, human) -> Optional[Type[Job]]:
        if human is None:
            return None
        return self.HUMAN_JOB_MAPPING.get(human.job)

    def _human_produces_object(self, job_cls: Type[Job], object_type: str) -> bool:
        return any(resource_type == object_type for resource_type, _ in job_cls.get_output())

    def _compute_unit_cost(self, human, job_cls: Type[Job]) -> float:
        time_cost = time_cost_per_unit(human, job_cls)
        input_cost = self._input_cost_per_unit(job_cls)
        return time_cost + input_cost

    def _input_cost_per_unit(self, job_cls: Type[Job]) -> float:
        total_cost = 0.0
        for resource_type, quantity in job_cls.get_input():
            if quantity <= 0:
                continue
            unit_price = self.price_reference.get_reference_price(resource_type)
            total_cost += unit_price * quantity
        return total_cost

    def _stock_effect(self, human, job_cls: Type[Job], object_type: str) -> float:
        n_days = self._equivalent_stock_days(human, job_cls, object_type)
        return min(n_days * self.STOCK_EFFECT, 1.0)

    def _equivalent_stock_days(self, human, job_cls: Type[Job], object_type: str) -> float:
        daily_output = self._daily_output_capacity(human, job_cls, object_type)
        if daily_output <= 0:
            return 0.0
        owned_quantity = human.owned_objects.filter(type=object_type).count()
        return owned_quantity / daily_output

    def _daily_output_capacity(self, human, job_cls: Type[Job], object_type: str) -> float:
        per_cycle_quantity = 0
        for resource_type, quantity in job_cls.get_output():
            if resource_type == object_type:
                per_cycle_quantity = quantity
                break
        if per_cycle_quantity <= 0:
            return 0.0

        without_tool, with_tool = JobCapacityService.compute_daily_capacity(job_cls)
        if job_cls.requires_tool() and job_cls.TOOL is not None:
            has_tool = human.owned_objects.filter(type=job_cls.TOOL).exists()
            actions_per_day = with_tool if has_tool else without_tool
        else:
            actions_per_day = without_tool

        if actions_per_day <= 0:
            return 0.0
        return per_cycle_quantity * actions_per_day
