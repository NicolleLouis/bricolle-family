from django.core.exceptions import ValidationError
from django.db.models import Avg

from the_bazaar.constants.character import Character
from the_bazaar.models import Season, Run
from the_bazaar.value_objects.aggregate_character_run import AggregateCharacterRunResult


class AggregateCharacterRunService:
    def __init__(self, character: str, run_range=None):
        self.character = character
        self.result = AggregateCharacterRunResult(character=Character(character).label)
        self.sanitize()
        self.runs = self.get_runs(run_range)
        self.compute()

    def sanitize(self):
        if self.character not in Character.values:
            raise ValueError(f"{self.character} is not a valid character.")

    def compute(self):
        self.compute_average_victory_number()
        self.compute_best_result()
        self.compute_elo_change()
        self.compute_run_number()

    def get_runs(self, run_range=None):
        if run_range is None or run_range == 'current_season':
            newest_season = Season.objects.order_by('-created_at').first()
            return Run.objects.filter(
                character=self.character,
                season=newest_season
            )
        elif run_range == 'all_time':
            return Run.objects.filter(character=self.character)
        else:
            raise ValidationError(f'run_range {run_range} not implemented')

    def compute_average_victory_number(self):
        average = self.runs.aggregate(
            average_victory_number=Avg('win_number')
        )['average_victory_number']
        if average is not None:
            average = round(average, 2)
        self.result.average_victory_number = average

    def compute_best_result(self):
        best_run = self.runs.order_by('-win_number').first()
        if best_run:
            self.result.best_result = best_run.get_result_display()

    def compute_run_number(self):
        self.result.run_number = len(self.runs)

    def compute_elo_change(self):
        elo_changes = [run.elo_change for run in self.runs]
        self.result.elo_change = sum(elo_changes)
