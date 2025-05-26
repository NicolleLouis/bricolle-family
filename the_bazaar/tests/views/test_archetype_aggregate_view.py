from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from the_bazaar.models import Archetype, Season, Run
from the_bazaar.constants.character import Character

class ArchetypeAggregateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.season = Season.objects.create(name="Test Season", version="1.0", start_date=timezone.now(), created_at=timezone.now())
        
        # Using valid character enum values
        self.arch1 = Archetype.objects.create(name="Meta Arch 1", character=Character.VANESSA.value, is_meta_viable=True)
        # Replaced Character.BRUTE with Character.DOOLEY
        self.arch2 = Archetype.objects.create(name="Non Meta Arch", character=Character.DOOLEY.value, is_meta_viable=False)
        # Replaced Character.HUNTRESS with Character.MAK
        self.arch3 = Archetype.objects.create(name="Meta Arch 2", character=Character.MAK.value, is_meta_viable=True)

        # Add some runs to make the page more realistic and test aggregation if necessary
        Run.objects.create(character=Character.VANESSA.value, archetype=self.arch1, win_number=10, season=self.season, elo_change=2)
        Run.objects.create(character=Character.MAK.value, archetype=self.arch3, win_number=5, season=self.season, elo_change=0)


    def test_archetype_stats_view_get(self):
        response = self.client.get(reverse('the_bazaar:archetype_stats'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'the_bazaar/aggregated_by_archetype.html')
        
        # Check that meta viable archetypes are in context
        self.assertContains(response, "Meta Arch 1")
        self.assertContains(response, "Meta Arch 2")
        # Check that non-meta viable archetypes are NOT in context
        self.assertNotContains(response, "Non Meta Arch")
        
        # Check for range options
        self.assertContains(response, "current_season")
        self.assertContains(response, "all_time")

        # Check if character names are displayed (using the label)
        self.assertContains(response, Character.VANESSA.label)
        self.assertContains(response, Character.MAK.label)


    def test_archetype_stats_view_with_range_param(self):
        response = self.client.get(reverse('the_bazaar:archetype_stats') + '?range=all_time')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'the_bazaar/aggregated_by_archetype.html')
        
        # Check that the active range is correctly reflected in the context/template
        # This could be by checking the 'active' class on the button if your template supports it,
        # or checking the value of 'current_range' in the context.
        # For simplicity, we'll assume the view passes 'current_range' correctly.
        # The template provided has: <a href="?range=all_time" class="btn btn-outline-primary {% if current_range == 'all_time' %}active{% endif %}"
        # So we can check for the active class.
        self.assertContains(response, 'href="?range=all_time"', msg_prefix="Link to all_time range not found")
        self.assertContains(response, 'class="btn btn-outline-primary active"', msg_prefix="All time button not marked active")
        
        # Check that meta viable archetypes are still present
        self.assertContains(response, "Meta Arch 1")
        self.assertContains(response, "Meta Arch 2")
        self.assertNotContains(response, "Non Meta Arch")

    def test_archetype_stats_view_empty_state(self):
        # Delete all archetypes to test the empty state
        Archetype.objects.all().delete()
        response = self.client.get(reverse('the_bazaar:archetype_stats'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No archetype data available for the selected period.")

    def test_archetype_stats_view_no_runs_for_archetype(self):
        # Create a meta viable archetype with no runs
        Archetype.objects.create(name="Meta NoRuns Arch", character=Character.PYGMALIEN.value, is_meta_viable=True)
        response = self.client.get(reverse('the_bazaar:archetype_stats'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Meta NoRuns Arch")
        # Check for default values displayed in the template for an archetype with no runs
        # Example: for "Meta NoRuns Arch", number of runs should be 0, avg_wins 0.00, best_result N/A
        # This requires inspecting the specific row for "Meta NoRuns Arch"
        # This is a bit more complex to assert correctly without more specific selectors in HTML,
        # but we can check for parts of the expected output.
        # Assuming the order is preserved or we parse the HTML, for now, let's check for key values.
        self.assertContains(response, "<td>0</td>", count=1) # Assuming only Meta NoRuns Arch has 0 runs
        self.assertContains(response, "<td>0.00</td>", count=1) # Assuming only Meta NoRuns Arch has 0.00 avg wins
        self.assertContains(response, "<td>N/A</td>", count=1) # Assuming only Meta NoRuns Arch has N/A best result

        # To make the above assertions more robust, let's ensure other archetypes have runs:
        # Meta Arch 1 had 1 run (win_number=10) -> 1 run, 10.00 avg, Gold win
        # Meta Arch 2 had 1 run (win_number=5) -> 1 run, 5.00 avg, Bronze win
        # So the count=1 assertions for 0, 0.00, N/A are specific to "Meta NoRuns Arch"
        # The template uses {{ info.average_victory_number|floatformat:2|default:"N/A" }}
        # and {{ info.best_result|default:"N/A" }}
        # and {{ info.run_number }}
        # The service sets these to 0, 0.0, "N/A" for no runs.
        # Let's refine the check for the specific row:
        expected_row_html_fragment = f"""
            <td>Meta NoRuns Arch</td>
            <td>{Character.PYGMALIEN.label}</td>
            <td>0</td>
            <td>0.00</td>
            <td>N/A</td>
            <td>0</td>
        """
        # Normalize whitespace for comparison
        normalized_expected_fragment = " ".join(expected_row_html_fragment.split())
        normalized_response_content = " ".join(response.content.decode().split())
        self.assertIn(normalized_expected_fragment, normalized_response_content)

        # Verify other data is still there
        self.assertContains(response, "Meta Arch 1")
        self.assertContains(response, Character.VANESSA.label)
        self.assertContains(response, "10.00") # Avg wins for Meta Arch 1
        self.assertContains(response, "Gold win") # Best result for Meta Arch 1

        self.assertContains(response, "Meta Arch 2")
        self.assertContains(response, Character.MAK.label)
        self.assertContains(response, "5.00") # Avg wins for Meta Arch 2
        self.assertContains(response, "Bronze win") # Best result for Meta Arch 2 (win_number 5)

        # Ensure the "0" for run_number was specific to "Meta NoRuns Arch"
        # Meta Arch 1 has 1 run, Meta Arch 2 has 1 run.
        # The table should look like:
        # Meta Arch 1 | Vanessa | 1 | 10.00 | Gold win | 2
        # Meta Arch 2 | Mak     | 1 | 5.00  | Bronze win | 0
        # Meta NoRuns Arch | Pygmalien | 0 | 0.00 | N/A | 0
        # So, "<td>0</td>" should appear twice (run_number for NoRuns, elo_change for Arch2)
        # "<td>0.00</td>" should appear once.
        # "<td>N/A</td>" should appear once.
        # Let's re-check counts based on this more complete table
        self.assertContains(response, "<td>0</td>", count=2) # run_number for NoRuns, elo_change for Arch2
        self.assertContains(response, "<td>0.00</td>", count=1) # avg_wins for NoRuns
        self.assertContains(response, "<td>N/A</td>", count=1) # best_result for NoRuns

        # Check elo_change for arch1 (2) and arch2 (0)
        self.assertContains(response, "<td>2</td>") # elo_change for Meta Arch 1
        # The second "<td>0</td>" is elo_change for Meta Arch 2 and run_number for NoRunsArch.
        # This means the previous count=2 for <td>0</td> is correct.
```
