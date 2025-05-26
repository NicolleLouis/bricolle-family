from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from the_bazaar.models import Run, Archetype, Season
from the_bazaar.services.aggregate_archetype_run import AggregateArchetypeRunService
from the_bazaar.constants.character import Character
from the_bazaar.value_objects.aggregate_archetype_run import AggregateArchetypeRunResult

class AggregateArchetypeRunServiceTest(TestCase):
    def setUp(self):
        # To ensure correct season ordering, make season2 strictly newer
        self.season1_start_date = timezone.now() - timedelta(days=60)
        self.season2_start_date = timezone.now() - timedelta(days=30)

        self.season1 = Season.objects.create(name="Season 1", version="1.0", start_date=self.season1_start_date, created_at=self.season1_start_date)
        self.season2 = Season.objects.create(name="Season 2", version="2.0", start_date=self.season2_start_date, created_at=self.season2_start_date)


        self.arch1 = Archetype.objects.create(name="Test Arch 1", character=Character.VANESSA.value)
        # The task description used Character.BRUTE, but this is not in the Character enum.
        # I'll use another valid character, e.g. Character.DOOLEY
        self.arch2 = Archetype.objects.create(name="Test Arch 2", character=Character.DOOLEY.value)


        # Runs for Arch1 - Season 2 (current by created_at)
        # Note: The Run model needs character, archetype, win_number, season, elo_change.
        # get_result_display() and elo changes are based on win_number.
        # win_number >= 10 -> Gold win, elo_change = 2
        # 7 <= win_number < 10 -> Silver win, elo_change = 1
        # 4 <= win_number < 7 -> Bronze win, elo_change = 0
        # win_number < 4 -> Loss, elo_change = -1
        Run.objects.create(character=Character.VANESSA.value, archetype=self.arch1, win_number=10, season=self.season2, elo_change=2) # Gold
        Run.objects.create(character=Character.VANESSA.value, archetype=self.arch1, win_number=5, season=self.season2, elo_change=0)  # Bronze
        
        # Runs for Arch1 - Season 1 (old)
        Run.objects.create(character=Character.VANESSA.value, archetype=self.arch1, win_number=7, season=self.season1, elo_change=1)  # Silver

        # Runs for Arch2 - Season 2 (current)
        Run.objects.create(character=Character.DOOLEY.value, archetype=self.arch2, win_number=3, season=self.season2, elo_change=-1)  # Loss

    def test_aggregate_current_season(self):
        # Ensure season2 is the newest for 'current_season' logic
        # This might require self.season2.save() if created_at is auto_now_add and not overridden in create
        # Or, if the service relies on `start_date`, ensure that's distinct and correctly ordered.
        # The service uses `order_by('-created_at').first()` for current season.
        # Let's explicitly update created_at if needed, or ensure it's set upon creation.
        # For this test, assuming created_at upon creation reflects the intended order.

        service = AggregateArchetypeRunService(archetype_id=self.arch1.id, run_range='current_season')
        result = service.result

        self.assertIsInstance(result, AggregateArchetypeRunResult)
        self.assertEqual(result.archetype_name, "Test Arch 1")
        self.assertEqual(result.character_name, Character.VANESSA.label)
        self.assertEqual(result.run_number, 2)
        self.assertEqual(result.average_victory_number, 7.5) # (10+5)/2
        self.assertEqual(result.best_result, "Gold win") # Based on win_number=10
        self.assertEqual(result.elo_change, 2) # Gold (+2) + Bronze (0) = 2

    def test_aggregate_all_time(self):
        service = AggregateArchetypeRunService(archetype_id=self.arch1.id, run_range='all_time')
        result = service.result

        self.assertEqual(result.run_number, 3) # Including season 1
        self.assertAlmostEqual(result.average_victory_number, round((10+5+7)/3, 2))
        self.assertEqual(result.best_result, "Gold win") # Still Gold from S2
        self.assertEqual(result.elo_change, 3) # Gold (+2) + Bronze (0) + Silver (+1) = 3

    def test_aggregate_no_runs(self):
        # The task description used Character.HUNTRESS, which is not in the Character enum.
        # I'll use another valid character, e.g. Character.MAK
        arch_no_runs = Archetype.objects.create(name="No Run Arch", character=Character.MAK.value)
        service = AggregateArchetypeRunService(archetype_id=arch_no_runs.id, run_range='current_season')
        result = service.result

        self.assertEqual(result.run_number, 0)
        self.assertEqual(result.average_victory_number, 0.0) 
        # The service default for best_result when no runs is "N/A"
        self.assertEqual(result.best_result, "N/A") 
        self.assertEqual(result.elo_change, 0)

    def test_nonexistent_archetype(self):
        with self.assertRaises(Archetype.DoesNotExist):
            AggregateArchetypeRunService(archetype_id=9999, run_range='current_season') # run_range is mandatory

    def test_invalid_range(self):
        with self.assertRaises(ValidationError): # Changed from Exception to ValidationError
             AggregateArchetypeRunService(archetype_id=self.arch1.id, run_range='invalid_range')
