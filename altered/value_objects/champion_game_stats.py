from dataclasses import dataclass
from altered.models import Champion


@dataclass
class ChampionGameStats:
    champion: Champion
    match_number: int = 0
    win_number: int = 0
    win_ratio: float = 0.0
