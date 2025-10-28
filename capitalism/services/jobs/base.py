from __future__ import annotations

from abc import ABC
from typing import Tuple, Optional

from capitalism.constants import ObjectType

# A resource bundle is a tuple of (object type, quantity) pairs.
ResourceBundle = Tuple[Tuple[ObjectType, int], ...]


class Job(ABC):
    """Abstract blueprint for concrete jobs performed by humans."""

    DURATION_MIN: int = 0
    INPUT: ResourceBundle = ()
    OUTPUT: ResourceBundle = ()
    TOOL: Optional[ObjectType] = None
    TOOL_EFFICIENCY: float = 1.0
    TOOL_BREAK_PROBABILITY: float = 0.0

    @classmethod
    def requires_tool(cls) -> bool:
        return cls.TOOL is not None

    @classmethod
    def get_input(cls) -> ResourceBundle:
        return cls.INPUT

    @classmethod
    def get_output(cls) -> ResourceBundle:
        return cls.OUTPUT
