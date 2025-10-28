from capitalism.constants import ObjectType

from .base import Job, ResourceBundle


class Miller(Job):
    DURATION_MIN: int = 60
    INPUT: ResourceBundle = ((ObjectType.WHEAT, 1), (ObjectType.WOOD, 1))
    OUTPUT: ResourceBundle = ((ObjectType.FLOUR, 1),)
    TOOL = None
    TOOL_EFFICIENCY: float = 1.0
    TOOL_BREAK_PROBABILITY: float = 0.0
