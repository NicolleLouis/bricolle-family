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
            # Re-raise the exception or handle as a ValueError, depending on desired API contract
            raise  # Or raise ValueError(f"Archetype with id {archetype_id} not found.")

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
                # Handle case where there are no seasons
                return runs_queryset.none() 
        elif self.run_range == 'all_time':
            return runs_queryset
        else:
            raise ValidationError(f'run_range "{self.run_range}" not implemented')

    def compute(self):
        self.compute_run_number() # Compute this first as other computations might depend on it or return early if 0
        if self.result.run_number == 0: # if no runs, no need to compute other stats
            self.result.average_victory_number = 0.0
            self.result.best_result = "N/A"
            self.result.elo_change = 0
            return

        self.compute_average_victory_number()
        self.compute_best_result()
        self.compute_elo_change()

    def compute_average_victory_number(self):
        average = self.runs.aggregate(
            average_victory_number=Avg('win_number')
        )['average_victory_number']
        if average is not None:
            average = round(average, 2)
        else:
            average = 0.0 # Default to 0.0 if no runs or win_number is null for all
        self.result.average_victory_number = average

    def compute_best_result(self):
        best_run = self.runs.order_by('-win_number').first()
        if best_run:
            self.result.best_result = best_run.get_result_display()
        else:
            self.result.best_result = "N/A" # Default if no runs

    def compute_run_number(self):
        self.result.run_number = self.runs.count() # More efficient than len(self.runs)

    def compute_elo_change(self):
        # Summing up elo_change. Assuming elo_change is a field on the Run model.
        # If elo_change can be None, we might need to handle that (e.g. Coalesce or filter None)
        # For now, assuming it's a non-nullable integer/float.
        total_elo_change = 0
        for run in self.runs: # Iterate if self.runs is already evaluated or small
             # If self.runs can be large, consider aggregate Sum
            if run.elo_change is not None:
                 total_elo_change += run.elo_change
        self.result.elo_change = total_elo_change
        # Alternative using Django ORM Sum if elo_change is a direct field and DB sum is preferred:
        # from django.db.models import Sum
        # elo_sum_data = self.runs.aggregate(total_elo=Sum('elo_change'))
        # self.result.elo_change = elo_sum_data['total_elo'] if elo_sum_data['total_elo'] is not None else 0
