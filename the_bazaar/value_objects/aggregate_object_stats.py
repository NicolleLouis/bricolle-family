import dataclasses


@dataclasses.dataclass
class AggregateObjectStatsResult:
    character: str
    total_objects: int = 0
    mastered_objects: int = 0
    mastered_ratio: float = 0.0
