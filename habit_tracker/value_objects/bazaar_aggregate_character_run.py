import dataclasses

from habit_tracker.constants.bazaar.result import Result


@dataclasses.dataclass
class BazaarAggregateCharacterRunResult:
    character: str
    average_victory_number: float = 0
    best_result: str = Result.LOSS.label
    elo_change: int = 0
    run_this_season: int = 0
