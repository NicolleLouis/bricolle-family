from capitalism.constants import ObjectType

from .base import Job, ResourceBundle


class ToolMaker(Job):
    DURATION_MIN: int = 600
    INPUT: ResourceBundle = (
        (ObjectType.WOOD, 1),
        (ObjectType.ORE, 1),
    )
    OUTPUT: ResourceBundle = (
        (ObjectType.PICKAXE, 1),
        (ObjectType.AXE, 1),
        (ObjectType.SCYTHE, 1),
        (ObjectType.SPATULA, 1),
    )
    TOOL = None
    TOOL_EFFICIENCY: float = 1.0
    TOOL_BREAK_PROBABILITY: float = 0.0
