from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from the_bazaar.models import Season, Archetype, Run
from the_bazaar.constants.character import Character
from the_bazaar.constants.result import Result
from the_bazaar.forms.archetype_filter import ArchetypeFilterForm # For context assertion

# Helper functions (can be defined within the TestCase or outside if preferred)
def get_character_label(character_value):
    return Character(character_value).label

def get_result_label(result_value):
    return Result(result_value).label

class BazaarAggregateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Seasons
        cls.current_season = Season.objects.create(name="Current Test Season", start_date=timezone.now() - timezone.timedelta(days=30), end_date=timezone.now() + timezone.timedelta(days=30))
        cls.previous_season = Season.objects.create(name="Previous Test Season", start_date=timezone.now() - timezone.timedelta(days=90), end_date=timezone.now() - timezone.timedelta(days=31))

        # Archetypes
        cls.arch_van_meta = Archetype.objects.create(name="Meta Vanessa", character=Character.VANESSA.value, is_meta_viable=True)
        cls.arch_leo_meta = Archetype.objects.create(name="Meta Leo", character=Character.LEO.value, is_meta_viable=True)
        cls.arch_van_non_meta = Archetype.objects.create(name="Non-Meta Vanessa", character=Character.VANESSA.value, is_meta_viable=False)
        cls.arch_zane_non_meta = Archetype.objects.create(name="Non-Meta Zane", character=Character.ZANE.value, is_meta_viable=False)
        cls.arch_leo_all_time = Archetype.objects.create(name="All Time Leo", character=Character.LEO.value, is_meta_viable=False) # Meta viable false but will have runs

        # Runs - associated with archetypes and seasons
        # Current Season Runs
        Run.objects.create(archetype=cls.arch_van_meta, season=cls.current_season, character_played=Character.VANESSA.value, win_number=7) # Gold win
        Run.objects.create(archetype=cls.arch_van_meta, season=cls.current_season, character_played=Character.VANESSA.value, win_number=6) # Silver win
        Run.objects.create(archetype=cls.arch_leo_meta, season=cls.current_season, character_played=Character.LEO.value, win_number=3) # Loss
        
        # Previous Season Runs
        Run.objects.create(archetype=cls.arch_van_non_meta, season=cls.previous_season, character_played=Character.VANESSA.value, win_number=7) # Gold win
        Run.objects.create(archetype=cls.arch_zane_non_meta, season=cls.previous_season, character_played=Character.ZANE.value, win_number=0) # Loss
        Run.objects.create(archetype=cls.arch_leo_all_time, season=cls.previous_season, character_played=Character.LEO.value, win_number=7) # Gold win for an otherwise non-meta archetype

        cls.client = Client()
        cls.url = reverse('aggregated_by_archetype')

    def test_meta_viability_current_season(self):
        response = self.client.get(self.url, {'range': 'current_season'})
        self.assertEqual(response.status_code, 200)
        aggregated_infos = response.context['aggregated_infos']
        # Expected: arch_van_meta, arch_leo_meta
        self.assertEqual(len(aggregated_infos), 2)
        names = sorted([info.archetype_name for info in aggregated_infos])
        self.assertIn(self.arch_van_meta.name, names)
        self.assertIn(self.arch_leo_meta.name, names)
        # Ensure no non-meta archetypes from current season (if they had runs) or any from previous
        self.assertNotIn(self.arch_van_non_meta.name, names)
        self.assertNotIn(self.arch_zane_non_meta.name, names)

    def test_meta_viability_all_time(self):
        response = self.client.get(self.url, {'range': 'all_time'})
        self.assertEqual(response.status_code, 200)
        aggregated_infos = response.context['aggregated_infos']
        # Expected: arch_van_meta, arch_leo_meta (from current), arch_van_non_meta, arch_zane_non_meta, arch_leo_all_time (from previous)
        # The view code filters by Archetype.objects.all() for all_time, then AggregateArchetypeRunService calculates stats.
        # If an archetype has no runs in "all_time" range, it won't appear in aggregated_infos.
        # All our archetypes with runs should appear.
        self.assertEqual(len(aggregated_infos), 5) # All archetypes that have runs
        names = sorted([info.archetype_name for info in aggregated_infos])
        self.assertIn(self.arch_van_meta.name, names)
        self.assertIn(self.arch_leo_meta.name, names)
        self.assertIn(self.arch_van_non_meta.name, names)
        self.assertIn(self.arch_zane_non_meta.name, names)
        self.assertIn(self.arch_leo_all_time.name, names)

    def test_sorting_by_archetype_name_default(self):
        response = self.client.get(self.url, {'range': 'all_time'}) # Using all_time for more data points
        self.assertEqual(response.status_code, 200)
        aggregated_infos = response.context['aggregated_infos']
        names = [info.archetype_name for info in aggregated_infos]
        self.assertEqual(names, sorted(names)) # Ascending
        self.assertEqual(response.context['current_orderby'], 'archetype_name')

    def test_sorting_by_archetype_name_explicit(self):
        response = self.client.get(self.url, {'range': 'all_time', 'orderby': 'archetype_name'})
        self.assertEqual(response.status_code, 200)
        aggregated_infos = response.context['aggregated_infos']
        names = [info.archetype_name for info in aggregated_infos]
        self.assertEqual(names, sorted(names))
        self.assertEqual(response.context['current_orderby'], 'archetype_name')

    def test_sorting_by_run_number(self):
        response = self.client.get(self.url, {'range': 'all_time', 'orderby': 'run_number'})
        self.assertEqual(response.status_code, 200)
        aggregated_infos = response.context['aggregated_infos']
        run_numbers = [info.run_number for info in aggregated_infos]
        self.assertEqual(run_numbers, sorted(run_numbers, reverse=True)) # Descending
        self.assertEqual(response.context['current_orderby'], 'run_number')
        # Check specific run numbers: arch_van_meta (2 runs), others (1 run)
        # Expected order might be: Meta Vanessa (2), then others with 1 run sorted by name (secondary sort not explicit)
        # The primary sort is run_number. Names might be in original DB order or Archetype name for ties.
        # The view sorts by run_number, then by archetype_name for ties (due to initial queryset order_by)
        self.assertEqual(aggregated_infos[0].archetype_name, self.arch_van_meta.name) # 2 runs
        self.assertEqual(aggregated_infos[0].run_number, 2)


    def test_character_filtering_vanessa(self):
        vanessa_label = get_character_label(Character.VANESSA.value)
        response = self.client.get(self.url, {'range': 'all_time', 'character': Character.VANESSA.value})
        self.assertEqual(response.status_code, 200)
        aggregated_infos = response.context['aggregated_infos']
        self.assertTrue(len(aggregated_infos) > 0) # Should have Vanessa archetypes
        for info in aggregated_infos:
            self.assertEqual(info.character_name, vanessa_label)
        # Expected: arch_van_meta, arch_van_non_meta
        self.assertEqual(len(aggregated_infos), 2)
        names = sorted([info.archetype_name for info in aggregated_infos])
        self.assertIn(self.arch_van_meta.name, names)
        self.assertIn(self.arch_van_non_meta.name, names)


    def test_best_result_filtering_gold_win(self):
        gold_win_enum_key = Result.GOLD_WIN.value
        gold_win_label = get_result_label(gold_win_enum_key)
        
        response = self.client.get(self.url, {'range': 'all_time', 'best_result': gold_win_enum_key})
        self.assertEqual(response.status_code, 200)
        aggregated_infos = response.context['aggregated_infos']
        
        self.assertTrue(len(aggregated_infos) > 0)
        for info in aggregated_infos:
            self.assertEqual(info.best_result, gold_win_label)
        
        # Expected archetypes with Gold Win in all_time:
        # arch_van_meta (run with 7 wins)
        # arch_van_non_meta (run with 7 wins)
        # arch_leo_all_time (run with 7 wins)
        self.assertEqual(len(aggregated_infos), 3)
        names = sorted([info.archetype_name for info in aggregated_infos])
        self.assertIn(self.arch_van_meta.name, names)
        self.assertIn(self.arch_van_non_meta.name, names)
        self.assertIn(self.arch_leo_all_time.name, names)

    def test_combined_filtering_and_sorting(self):
        # Current season, Vanessa, Gold Win, sort by run_number (though only one expected)
        vanessa_enum_key = Character.VANESSA.value
        gold_win_enum_key = Result.GOLD_WIN.value

        params = {
            'range': 'current_season',
            'character': vanessa_enum_key,
            'best_result': gold_win_enum_key,
            'orderby': 'run_number'
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        aggregated_infos = response.context['aggregated_infos']

        # Expected: arch_van_meta (has a 7-win run in current season)
        self.assertEqual(len(aggregated_infos), 1)
        if aggregated_infos: # avoid error if empty
            info = aggregated_infos[0]
            self.assertEqual(info.archetype_name, self.arch_van_meta.name)
            self.assertEqual(info.character_name, get_character_label(vanessa_enum_key))
            self.assertEqual(info.best_result, get_result_label(gold_win_enum_key))
            # arch_van_meta has 2 runs in current season, one gold, one silver. Best is Gold.
            self.assertEqual(info.run_number, 2) 
        
        self.assertEqual(response.context['current_range'], 'current_season')
        self.assertEqual(response.context['current_orderby'], 'run_number')
        self.assertIsInstance(response.context['filter_form'], ArchetypeFilterForm)
        self.assertEqual(response.context['filter_form'].cleaned_data['character'], vanessa_enum_key)
        self.assertEqual(response.context['filter_form'].cleaned_data['best_result'], gold_win_enum_key)


    def test_context_data_presence(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('filter_form', response.context)
        self.assertIsInstance(response.context['filter_form'], ArchetypeFilterForm)
        self.assertIn('current_range', response.context)
        self.assertEqual(response.context['current_range'], 'current_season') # Default
        self.assertIn('current_orderby', response.context)
        self.assertEqual(response.context['current_orderby'], 'archetype_name') # Default
        self.assertIn('range_options', response.context)
        self.assertEqual(response.context['range_options'], ["current_season", "all_time"])

    def test_empty_results_with_filters(self):
        # Use a filter combination that yields no results
        # E.g., Zane (who only has runs in previous_season) with "current_season"
        zane_enum_key = Character.ZANE.value
        response = self.client.get(self.url, {'range': 'current_season', 'character': zane_enum_key})
        self.assertEqual(response.status_code, 200)
        aggregated_infos = response.context['aggregated_infos']
        self.assertEqual(len(aggregated_infos), 0)
        self.assertContains(response, "No archetype data available for the selected period.")

    def test_filter_form_in_context_has_data_from_get(self):
        leo_enum_key = Character.LEO.value
        silver_win_enum_key = Result.SILVER_WIN.value
        params = {
            'range': 'all_time',
            'character': leo_enum_key,
            'best_result': silver_win_enum_key, # Leo doesn't have Silver, so this will test form data
            'orderby': 'run_number'
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        
        filter_form_context = response.context['filter_form']
        self.assertIsInstance(filter_form_context, ArchetypeFilterForm)
        
        # Check that the form in context is bound and has the GET data
        self.assertTrue(filter_form_context.is_bound)
        self.assertEqual(filter_form_context.cleaned_data.get('character'), leo_enum_key)
        self.assertEqual(filter_form_context.cleaned_data.get('best_result'), silver_win_enum_key)
        
        # Even if results are empty, the form should reflect the query
        aggregated_infos = response.context['aggregated_infos']
        # Meta Leo (current) has 1 loss (3 wins). All Time Leo (previous) has 1 gold (7 wins)
        # So no Leo with Silver Win.
        self.assertEqual(len(aggregated_infos), 0)
        self.assertContains(response, "No archetype data available for the selected period.")
```

A note on `AggregateArchetypeRunService`: These tests are for the view logic. The `AggregateArchetypeRunService` is assumed to be working correctly (it should have its own unit tests, though that's outside the scope of this specific subtask). The view tests focus on whether the view correctly *uses* the service and manages data flow, filtering, sorting, and context.

For the `test_sorting_by_run_number`, I added a small check for the `arch_van_meta` since it has 2 runs in the current season, and thus its `run_number` from the service should be 2. The others created in `setUpTestData` for `current_season` have 1 run each. For `all_time`, `arch_van_meta` still has 2 runs, `arch_van_non_meta` has 1, `arch_leo_meta` has 1, `arch_zane_non_meta` has 1, `arch_leo_all_time` has 1. So `arch_van_meta` should come first when sorting by `run_number` descending.

I've included tests for default sorting, explicit sorting, filtering by character, filtering by best result, a combination of these, context data, and empty results. This should cover the view logic comprehensively.The tests for `ArchetypeFilterForm` in `the_bazaar/tests/test_forms.py` were created in the previous step.
The tests for the view logic (`BazaarAggregate.by_archetype`) in `the_bazaar/tests/test_views.py` were also created in the previous step.

Both sets of tests are now in place according to the subtask description.
The `test_forms.py` includes:
-   Validity checks for various data inputs (empty, partial, full, invalid).
-   Cleaned data checks.
-   Widget attribute checks.
-   Presence of empty choices and all enum choices.

The `test_views.py` includes:
-   `setUpTestData` to create `Season`, `Archetype`, and `Run` instances.
-   Tests for meta viability filtering (`range` parameter).
-   Tests for sorting (`orderby` parameter, including default).
-   Tests for character filtering.
-   Tests for best result filtering (checking enum key vs. label).
-   Tests for combined functionality (multiple parameters).
-   Tests for correct context data passed to the template.
-   Tests for graceful handling of scenarios leading to no results.
-   Tests that the `filter_form` in context is correctly populated from GET parameters.

All specified test scenarios seem to be covered. I can now submit the report.
