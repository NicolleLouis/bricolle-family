from django.core.exceptions import ValidationError
from django.db.models import Avg

from the_bazaar.constants.character import Character
from the_bazaar.models import Season, Run
from the_bazaar.models.archetype import Archetype
from the_bazaar.value_objects.aggregate_archetype_run import AggregateArchetypeRunResult


class AggregateArchetypeRunService:
    def __init__(self, archetype_id: int, run_range: str = 'current_season'):
        self.archetype_id = archetype_id
        self.run_range = run_range

        try:
            self.archetype = Archetype.objects.get(id=self.archetype_id)
        except Archetype.DoesNotExist:
            raise ValueError(f"Archetype with id {archetype_id} not found.")

        character_display_name = Character(self.archetype.character).label
        self.result = AggregateArchetypeRunResult(
            archetype_name=self.archetype.name,
            character_name=character_display_name
        )

        self.runs = self.get_runs()
        self.compute()

    def get_runs(self):
        runs_queryset = Run.objects.filter(archetype=self.archetype)

        if self.run_range == 'current_season':
            newest_season = Season.objects.order_by('-created_at').first()
            if newest_season:
                return runs_queryset.filter(season=newest_season)
            else:
                return runs_queryset.none()
        elif self.run_range == 'all_time':
            return runs_queryset
        else:
            raise ValidationError(f'run_range "{self.run_range}" not implemented')

    def compute(self):
        self.compute_run_number()
        if self.result.run_number == 0:
            self.result.average_victory_number = 0.0
            self.result.best_result = "N/A"
            self.result.elo_change = 0
            return

        self.compute_average_victory_number()
        self.compute_win_number()
        self.compute_best_result()
        self.compute_elo_change()

    def compute_average_victory_number(self):
        average = self.runs.aggregate(
            average_victory_number=Avg('win_number')
        )['average_victory_number']
        if average is not None:
            average = round(average, 2)
        else:
            average = 0.0
        self.result.average_victory_number = average

    def compute_win_number(self):
        self.result.win_number = self.runs.filter(win_number=10).count()

    def compute_best_result(self):
        best_run = self.runs.order_by('-win_number').first()
        if best_run:
            self.result.best_result = best_run.get_result_display()
        else:
            self.result.best_result = "N/A"

    def compute_run_number(self):
        self.result.run_number = self.runs.count()

    def compute_elo_change(self):
        total_elo_change = 0
        for run in self.runs:
            if run.elo_change is not None:
                 total_elo_change += run.elo_change
        self.result.elo_change = total_elo_change
