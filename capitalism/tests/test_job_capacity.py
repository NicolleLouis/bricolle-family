from capitalism.services import Job, Miner, JobCapacityService


class NoToolJob(Job):
    DURATION_MIN = 120
    TOOL = None
    TOOL_EFFICIENCY = 2.0


class ZeroDurationJob(Job):
    DURATION_MIN = 0


def test_miner_capacity_with_and_without_tool():
    without_tool, with_tool = JobCapacityService.compute_daily_capacity(Miner)

    assert without_tool == 1
    assert with_tool == 10


def test_job_without_tool_returns_same_capacity():
    without_tool, with_tool = JobCapacityService.compute_daily_capacity(NoToolJob)

    assert without_tool == 5
    assert with_tool == 5


def test_zero_duration_job_has_zero_capacity():
    without_tool, with_tool = JobCapacityService.compute_daily_capacity(ZeroDurationJob)

    assert without_tool == 0
    assert with_tool == 0
