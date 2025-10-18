from dataclasses import dataclass


@dataclass
class ObjectiveProgress:
    percentage: float
    completed_value: int = 0
    total_value: int = 0
    current_streak: int = 0
    streak_target: int = 0
    status_success: bool = False
    progress_description: str = ""
