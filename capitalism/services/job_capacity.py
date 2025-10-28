from __future__ import annotations

from math import floor
from typing import Tuple, Type

from capitalism.services.jobs.base import Job


class JobCapacityService:
    WORK_MINUTES_PER_DAY = 10 * 60  # 10 hours

    @classmethod
    def compute_daily_capacity(cls, job_cls: Type[Job]) -> Tuple[int, int]:
        """Return (#jobs without a tool, #jobs with tool) for a single day."""
        duration = job_cls.DURATION_MIN
        if duration <= 0:
            return 0, 0

        without_tool = cls.WORK_MINUTES_PER_DAY // duration

        if not job_cls.requires_tool():
            return without_tool, without_tool

        efficiency = job_cls.TOOL_EFFICIENCY
        if efficiency is None or efficiency <= 0:
            return without_tool, without_tool

        effective_duration = duration / efficiency
        if effective_duration <= 0:
            with_tool = without_tool
        else:
            with_tool = floor(cls.WORK_MINUTES_PER_DAY / effective_duration)

        return without_tool, max(with_tool, 0)
