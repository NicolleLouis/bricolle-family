from __future__ import annotations

import random
from typing import TYPE_CHECKING

from capitalism.constants.jobs import Job
from capitalism.constants.simulation_step import SimulationStep
from capitalism.services import (
    JobCapacityService,
    JobInventoryService,
    Miner,
    Lumberjack,
    ToolMaker,
    Farmer,
    Miller,
    Baker,
)

if TYPE_CHECKING:
    from capitalism.models import Human


class HumanWithoutJobException(RuntimeError):
    """Raised when attempting production for a human without a configured job."""


class MissingObjectInput(RuntimeError):
    """Raised when production cannot consume the required input objects."""


class ProductionService:
    JOB_CLASS_MAPPING = {
        Job.MINER: Miner,
        Job.LUMBERJACK: Lumberjack,
        Job.TOOLMAKER: ToolMaker,
        Job.FARMER: Farmer,
        Job.MILLER: Miller,
        Job.BAKER: Baker,
    }

    random_generator = random.Random()

    def __init__(self, human: "Human"):
        self.human = human

    def run(self) -> SimulationStep:
        job_cls = self._get_job_class()
        if job_cls is None:
            raise HumanWithoutJobException(
                f"Human {self.human.id} does not have a configured job."
            )

        time_capacity = self._time_capacity(job_cls)
        input_capacity = JobInventoryService.compute_input_capacity(self.human, job_cls)

        capacities = [time_capacity]
        if input_capacity is not None:
            capacities.append(input_capacity)

        max_actions = min(capacities) if capacities else 0

        if max_actions <= 0:
            return self._advance_step()

        self._consume_inputs(job_cls, max_actions)
        self._produce_outputs(job_cls, max_actions)
        self._handle_tool_wear(job_cls)

        return self._advance_step()

    def _advance_step(self) -> SimulationStep:
        return self.human.next_step()

    def _get_job_class(self):
        return self.JOB_CLASS_MAPPING.get(self.human.job)

    def _time_capacity(self, job_cls) -> int:
        without_tool, with_tool = JobCapacityService.compute_daily_capacity(job_cls)
        if not job_cls.requires_tool():
            return without_tool
        elif self.human.has_object(job_cls.TOOL):
            return with_tool
        return without_tool

    def _has_tool(self, tool_type) -> bool:
        if tool_type is None:
            return True
        return self.human.has_object(tool_type)

    def _consume_inputs(self, job_cls, max_actions: int):
        for object_type, quantity in job_cls.get_input():
            total_needed = quantity * max_actions
            removed = self.human.remove_objects(object_type, total_needed)
            if removed < total_needed:
                raise MissingObjectInput(
                    f"Insufficient inventory for {object_type} while processing production."
                )

    def _produce_outputs(self, job_cls, max_actions: int):
        for object_type, quantity in job_cls.get_output():
            total_to_create = quantity * max_actions
            self.human.add_objects(object_type, total_to_create)

    def _handle_tool_wear(self, job_cls):
        if not job_cls.requires_tool():
            return

        probability = getattr(job_cls, "TOOL_BREAK_PROBABILITY", 0) or 0
        if probability <= 0:
            return

        tool_type = job_cls.TOOL
        if not self.human.has_object(tool_type):
            return

        if self._should_break_tool(probability):
            self.human.remove_objects(tool_type, 1)

    def _should_break_tool(self, probability: float) -> bool:
        return self.random_generator.random() < probability
