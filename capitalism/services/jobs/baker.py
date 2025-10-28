from capitalism.constants import ObjectType

from .base import Job, ResourceBundle


class Baker(Job):
    DURATION_MIN: int = 60
    INPUT: ResourceBundle = ((ObjectType.FLOUR, 1), (ObjectType.WOOD, 1))
    OUTPUT: ResourceBundle = ((ObjectType.BREAD, 1),)
    TOOL = ObjectType.SPATULA
    TOOL_EFFICIENCY: float = 2
    TOOL_BREAK_PROBABILITY: float = 0.01
