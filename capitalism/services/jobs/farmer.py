from capitalism.constants import ObjectType

from .base import Job, ResourceBundle


class Farmer(Job):
    DURATION_MIN: int = 60
    INPUT: ResourceBundle = ()
    OUTPUT: ResourceBundle = (
        (ObjectType.WHEAT, 1),
    )
    TOOL = ObjectType.SCYTHE
    TOOL_EFFICIENCY: float = 1.0
    TOOL_BREAK_PROBABILITY: float = 0.01
