import dataclasses


@dataclasses.dataclass
class BazaarAggregateCharacterRunResult:
    average_victory: float
    best_result: str
    character: str
    elo_change: int
    run_this_season: int
