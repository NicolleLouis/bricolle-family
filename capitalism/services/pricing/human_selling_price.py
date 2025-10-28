from __future__ import annotations

from typing import Optional, Type

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


class HumanSellingPriceValuationService:
    """Estimate the selling price a human is willing to ask for a produced object."""

    TIME_COST_PER_HOUR = 1.2
    MARKUP_BASE = 0.2
    STOCK_SENSITIVITY = 0.05

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
        markup = self._base_markup()
        stock_adjustment = self._stock_adjustment(human, job_cls, object_type)

        raw_price = unit_cost * (1 + markup + stock_adjustment)
        return max(0.01, raw_price)

    def _human_job_class(self, human) -> Optional[Type[Job]]:
        if human is None:
            return None
        return self.HUMAN_JOB_MAPPING.get(human.job)

    def _human_produces_object(self, job_cls: Type[Job], object_type: str) -> bool:
        return any(resource_type == object_type for resource_type, _ in job_cls.get_output())

    def _compute_unit_cost(self, human, job_cls: Type[Job]) -> float:
        time_cost = self._time_cost_per_unit(human, job_cls)
        input_cost = self._input_cost_per_unit(job_cls)
        return time_cost + input_cost

    def _time_cost_per_unit(self, human, job_cls: Type[Job]) -> float:
        duration_minutes = job_cls.DURATION_MIN
        if job_cls.requires_tool() and self._human_has_tool(human, job_cls.TOOL):
            efficiency = job_cls.TOOL_EFFICIENCY or 1
            if efficiency > 0:
                duration_minutes = duration_minutes / efficiency

        hours = duration_minutes / 60
        return hours * self.TIME_COST_PER_HOUR

    def _input_cost_per_unit(self, job_cls: Type[Job]) -> float:
        total_cost = 0.0
        for resource_type, quantity in job_cls.get_input():
            if quantity <= 0:
                continue
            unit_price = self.price_reference.get_reference_price(resource_type)
            total_cost += unit_price * quantity
        return total_cost

    def _base_markup(self) -> float:
        return self.MARKUP_BASE

    def _stock_adjustment(self, human, job_cls: Type[Job], object_type: str) -> float:
        target_quantity = JobTargetService.compute_target_quantity(job_cls, object_type)
        current_quantity = human.owned_objects.filter(type=object_type).count()
        return self.STOCK_SENSITIVITY * (target_quantity - current_quantity)

    @staticmethod
    def _human_has_tool(human, tool_type: Optional[str]) -> bool:
        if tool_type is None:
            return False
        return human.owned_objects.filter(type=tool_type).exists()
