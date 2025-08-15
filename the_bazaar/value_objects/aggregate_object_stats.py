import dataclasses


@dataclasses.dataclass
class AggregateObjectStatsResult:
    character: str
    total_objects: int = 0
    winning_objects: int = 0
    winning_ratio: float = 0.0
