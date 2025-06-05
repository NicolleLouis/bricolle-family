from dataclasses import dataclass
from altered.models import Deck


@dataclass
class DeckGameStats:
    deck: Deck
    match_number: int = 0
    win_number: int = 0
    win_ratio: float = 0.0
