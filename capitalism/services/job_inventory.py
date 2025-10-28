from __future__ import annotations

from typing import Optional, Type

from capitalism.services.jobs.base import Job


class JobInventoryService:
    """Utility helpers for evaluating job input availability."""

    @staticmethod
    def compute_input_capacity(human, job_cls: Type[Job]) -> Optional[int]:
        """Determine how many actions the human can perform based on their inventory."""
        inputs = job_cls.get_input()
        if not inputs:
            return None

        capacities = []
        for object_type, quantity in inputs:
            if quantity <= 0:
                capacities.append(float("inf"))
                continue

            available = human.owned_objects.filter(type=object_type).count()
            capacities.append(available // quantity)

        if not capacities:
            return None

        return min(capacities)
