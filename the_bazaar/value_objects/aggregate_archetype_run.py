from dataclasses import dataclass, field

@dataclass
class AggregateArchetypeRunResult:
    archetype_name: str
    character_name: str
    run_number: int = 0
    average_victory_number: float = None
    best_result: str = None
    elo_change: int = 0
