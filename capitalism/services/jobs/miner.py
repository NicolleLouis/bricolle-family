from capitalism.constants import ObjectType

from .base import Job, ResourceBundle


class Miner(Job):
    DURATION_MIN: int = 600
    INPUT: ResourceBundle = ()
    OUTPUT: ResourceBundle = ((ObjectType.ORE, 1),)
    TOOL = ObjectType.PICKAXE
    TOOL_EFFICIENCY: float = 10
    TOOL_BREAK_PROBABILITY: float = 0.01
