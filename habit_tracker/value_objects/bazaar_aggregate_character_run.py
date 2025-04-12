import dataclasses


@dataclasses.dataclass
class BazaarAggregateCharacterRunResult:
    character: str
    average_victory_number: float = 0
    best_result: str = "No run"
    elo_change: int = 0
    run_number: int = 0
