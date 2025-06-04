from the_bazaar.constants.character import Character
from the_bazaar.models import Object
from the_bazaar.value_objects.aggregate_object_stats import AggregateObjectStatsResult


class AggregateObjectStatsService:
    def __init__(self, character: str | None = None):
        self.character = character
        self.sanitize()
        label = Character(character).label if character else "All"
        self.result = AggregateObjectStatsResult(character=label)
        self.objects = self.get_objects()
        self.compute()

    def sanitize(self):
        if self.character is not None and self.character not in Character.values:
            raise ValueError(f"{self.character} is not a valid character.")

    def get_objects(self):
        if self.character:
            return Object.objects.filter(character=self.character)
        return Object.objects.all()

    def compute(self):
        self.compute_total_objects()
        self.compute_mastered_objects()
        self.compute_mastered_ratio()

    def compute_total_objects(self):
        self.result.total_objects = self.objects.count()

    def compute_mastered_objects(self):
        self.result.mastered_objects = self.objects.filter(was_mastered=True).count()

    def compute_mastered_ratio(self):
        if self.result.total_objects == 0:
            self.result.mastered_ratio = 0.0
        else:
            ratio = self.result.mastered_objects / self.result.total_objects * 100
            self.result.mastered_ratio = round(ratio, 2)
