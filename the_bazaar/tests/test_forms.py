from django.test import TestCase
from the_bazaar.forms.archetype_filter import ArchetypeFilterForm
from the_bazaar.constants.character import Character
from the_bazaar.constants.result import Result

class ArchetypeFilterFormTest(TestCase):
    def test_form_valid_no_data(self):
        """Test form is valid with no data (all fields optional)."""
        form = ArchetypeFilterForm({})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('character'), '')
        self.assertEqual(form.cleaned_data.get('best_result'), '')

    def test_form_valid_with_character_data(self):
        """Test form is valid with character data."""
        # Assuming Character.VANESSA is a valid choice
        character_value = Character.choices[0][0] # Get the first character value
        form = ArchetypeFilterForm({'character': character_value})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['character'], character_value)

    def test_form_valid_with_best_result_data(self):
        """Test form is valid with best_result data."""
        # Assuming Result.GOLD_WIN is a valid choice
        result_value = Result.choices[0][0] # Get the first result value
        form = ArchetypeFilterForm({'best_result': result_value})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['best_result'], result_value)

    def test_form_valid_with_character_and_best_result_data(self):
        """Test form is valid with both character and best_result data."""
        character_value = Character.choices[0][0]
        result_value = Result.choices[0][0]
        form = ArchetypeFilterForm({
            'character': character_value,
            'best_result': result_value
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['character'], character_value)
        self.assertEqual(form.cleaned_data['best_result'], result_value)

    def test_form_cleaned_data_empty_strings(self):
        """Test cleaned_data for empty selections."""
        form = ArchetypeFilterForm({'character': '', 'best_result': ''})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['character'], '')
        self.assertEqual(form.cleaned_data['best_result'], '')

    def test_form_invalid_character_data(self):
        """Test form with an invalid character value."""
        form = ArchetypeFilterForm({'character': 'INVALID_CHARACTER'})
        # The form should still be "valid" because the ChoiceField will
        # coerce invalid choices to an empty string if validation doesn't strictly
        # enforce choices on the server-side for non-required fields, 
        # or it might be invalid if choices are strictly enforced.
        # Django's default for ChoiceField is to validate against choices.
        self.assertFalse(form.is_valid()) 
        self.assertIn('character', form.errors)

    def test_form_invalid_best_result_data(self):
        """Test form with an invalid best_result value."""
        form = ArchetypeFilterForm({'best_result': 'INVALID_RESULT'})
        self.assertFalse(form.is_valid())
        self.assertIn('best_result', form.errors)

    def test_form_widget_attrs(self):
        """Test that widgets have the correct CSS class."""
        form = ArchetypeFilterForm()
        self.assertEqual(form.fields['character'].widget.attrs['class'], 'form-select')
        self.assertEqual(form.fields['best_result'].widget.attrs['class'], 'form-select')

    def test_form_choices_include_empty(self):
        """Test that choices include an empty choice."""
        form = ArchetypeFilterForm()
        self.assertEqual(form.fields['character'].choices[0][0], '')
        self.assertEqual(form.fields['character'].choices[0][1], 'All Characters')
        self.assertEqual(form.fields['best_result'].choices[0][0], '')
        self.assertEqual(form.fields['best_result'].choices[0][1], 'All Results')

    def test_form_all_character_choices_present(self):
        form = ArchetypeFilterForm()
        # First choice is empty, so +1
        self.assertEqual(len(form.fields['character'].choices), len(Character.choices) + 1)
        # Check a few specific choices
        for char_key, char_label in Character.choices:
            self.assertIn((char_key, char_label), form.fields['character'].choices)
            
    def test_form_all_result_choices_present(self):
        form = ArchetypeFilterForm()
        self.assertEqual(len(form.fields['best_result'].choices), len(Result.choices) + 1)
        for res_key, res_label in Result.choices:
            self.assertIn((res_key, res_label), form.fields['best_result'].choices)
