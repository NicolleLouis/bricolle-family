from capitalism.constants import ObjectType
from capitalism.services import (
    Job,
    Miner,
    Lumberjack,
    ToolMaker,
    Farmer,
    Miller,
    Baker,
)


class Woodcutting(Job):
    DURATION_MIN = 60
    INPUT = ((ObjectType.BREAD, 1),)
    OUTPUT = ((ObjectType.WOOD, 1),)
    TOOL = ObjectType.AXE
    TOOL_EFFICIENCY = 1.25
    TOOL_BREAK_PROBABILITY = 0.05


def test_job_constants_exposed():
    assert Woodcutting.DURATION_MIN == 60
    assert Woodcutting.get_input() == ((ObjectType.BREAD, 1),)
    assert Woodcutting.get_output() == ((ObjectType.WOOD, 1),)
    assert Woodcutting.requires_tool() is True
    assert Woodcutting.TOOL_EFFICIENCY == 1.25
    assert Woodcutting.TOOL_BREAK_PROBABILITY == 0.05


def test_registered_jobs_have_defaults():
    for job_cls in (Miner, Lumberjack, ToolMaker, Farmer, Miller, Baker):
        assert job_cls.DURATION_MIN > 0
        assert job_cls.TOOL_EFFICIENCY > 0
        assert 0 <= job_cls.TOOL_BREAK_PROBABILITY <= 1
