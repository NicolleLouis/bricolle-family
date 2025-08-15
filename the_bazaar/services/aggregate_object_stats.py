from the_bazaar.constants.character import Character
from the_bazaar.constants.result import Result
from the_bazaar.models import Object
from the_bazaar.value_objects.aggregate_object_stats import AggregateObjectStatsResult


class AggregateObjectStatsService:
    def __init__(self, character: str | None = None, victory_type: str = Result.GOLD_WIN):
        self.character = character
        self.victory_type = victory_type
        self.sanitize()
        label = Character(character).label if character else "All"
        self.result = AggregateObjectStatsResult(character=label)
        self.objects = self.get_objects()
        self.compute()

    def sanitize(self):
        if self.character is not None and self.character not in Character.values:
            raise ValueError(f"{self.character} is not a valid character.")
        if self.victory_type not in Result.values:
            raise ValueError(f"{self.victory_type} is not a valid result.")

    def get_objects(self):
        if self.character:
            return Object.objects.filter(character=self.character)
        return Object.objects.all()

    def compute(self):
        self.compute_total_objects()
        self.compute_winning_objects()
        self.compute_winning_ratio()

    def compute_total_objects(self):
        self.result.total_objects = self.objects.count()

    def compute_winning_objects(self):
        allowed = [Result.GOLD_WIN]
        if self.victory_type in (Result.SILVER_WIN, Result.BRONZE_WIN):
            allowed.append(Result.SILVER_WIN)
        if self.victory_type == Result.BRONZE_WIN:
            allowed.append(Result.BRONZE_WIN)
        self.result.winning_objects = self.objects.filter(best_win__in=allowed).count()

    def compute_winning_ratio(self):
        if self.result.total_objects == 0:
            self.result.winning_ratio = 0.0
        else:
            ratio = self.result.winning_objects / self.result.total_objects * 100
            self.result.winning_ratio = round(ratio, 2)
