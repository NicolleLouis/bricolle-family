import dataclasses


@dataclasses.dataclass
class Character:
    total_life: float = 0
    dps: float = 0
    hps: float = 0
    pps: float = 0
    name: str = None
    display_name: str = None
