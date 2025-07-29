from dataclasses import dataclass

from altered.models import Champion


@dataclass
class CareerChampionStats:
    champion: Champion
    win_number: int = 0
