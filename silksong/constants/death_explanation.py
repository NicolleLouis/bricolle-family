from silksong.constants import Boss, Arena, Location

DEATH_EXPLANATION_CHOICES = tuple(
    list(Boss.choices) + list(Arena.choices) + list(Location.choices)
)
