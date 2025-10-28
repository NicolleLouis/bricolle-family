from capitalism.constants import ObjectType
from capitalism.services import Farmer, JobTargetService


def test_target_for_base_need_and_input():
    bread_target = JobTargetService.compute_target_quantity(Farmer, ObjectType.BREAD)

    assert bread_target == 2


def test_target_for_tool():
    scythe_target = JobTargetService.compute_target_quantity(Farmer, ObjectType.SCYTHE)

    assert scythe_target == 2


def test_target_for_unrelated_object_is_zero():
    wheat_target = JobTargetService.compute_target_quantity(Farmer, ObjectType.WHEAT)

    assert wheat_target == 0


def test_target_for_base_need_only():
    wood_target = JobTargetService.compute_target_quantity(Farmer, ObjectType.WOOD)

    assert wood_target == 2
