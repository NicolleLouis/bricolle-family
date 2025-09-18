from .arena import Arena
from .boss import Boss
from .game_session_type import GameSessionType
from .location import Location

DEATH_EXPLANATION_CHOICES = tuple(
    list(Boss.choices) + list(Arena.choices) + list(Location.choices)
)
