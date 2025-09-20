from dataclasses import dataclass
from typing import Optional

from altered.models import Champion


@dataclass
class ChampionWinRate:
    champion: Champion
    match_number: int = 0
    win_number: int = 0
    win_ratio: Optional[float] = None
    ratio_color: str = "#e9ecef"
    ratio_text_color: str = "#212529"
    achievement_color: str = "#adb5bd"

    @property
    def has_game(self) -> bool:
        return self.match_number > 0

    @property
    def has_win(self) -> bool:
        return self.win_number > 0
