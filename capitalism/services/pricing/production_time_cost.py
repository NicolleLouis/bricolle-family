from __future__ import annotations

from typing import Type

from capitalism.constants.economy import TIME_COST_PER_HOUR
from capitalism.services.jobs.base import Job


def time_cost_per_unit(
    human,
    job_cls: Type[Job],
) -> float:

    duration_minutes = getattr(job_cls, "DURATION_MIN", 0) or 0

    if job_cls.requires_tool():
        tool_type = getattr(job_cls, "TOOL", None)
        if tool_type and human.owned_objects.filter(type=tool_type).exists():
            efficiency = getattr(job_cls, "TOOL_EFFICIENCY", 1) or 1
            if efficiency > 0:
                duration_minutes = duration_minutes / efficiency

    hours = duration_minutes / 60
    return hours * TIME_COST_PER_HOUR
