from __future__ import annotations

from typing import Type

from capitalism.constants import BASE_NEEDS, ObjectType
from capitalism.services.job_capacity import JobCapacityService
from capitalism.services.jobs.base import Job


class JobTargetService:
    """Utilities for computing desired inventory targets for job resources."""

    @classmethod
    def compute_target_quantity(cls, job_cls: Type[Job], object_type: ObjectType) -> int:
        """
        Compute the desired stock quantity for the given object type to support
        two efficient work days for the provided job.
        """
        target = 0

        for need_type, quantity in BASE_NEEDS:
            if need_type == object_type:
                target += quantity * 2
                break

        for input_type, quantity in job_cls.get_input():
            if input_type == object_type:
                _, with_tool = JobCapacityService.compute_daily_capacity(job_cls)
                target += quantity * with_tool * 2
                break

        if job_cls.requires_tool() and job_cls.TOOL == object_type:
            target = max(target, 2)

        return target
