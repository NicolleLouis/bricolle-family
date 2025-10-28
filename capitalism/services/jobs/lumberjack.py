from capitalism.constants import ObjectType

from .base import Job, ResourceBundle


class Lumberjack(Job):
    DURATION_MIN: int = 120
    INPUT: ResourceBundle = ()
    OUTPUT: ResourceBundle = ((ObjectType.WOOD, 1),)
    TOOL = ObjectType.AXE
    TOOL_EFFICIENCY: float = 4
    TOOL_BREAK_PROBABILITY: float = 0.01
