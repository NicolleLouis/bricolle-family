import pytest

from flash_cards.models import Category, Question, ThemePreset
from flash_cards.services import ThemePresetQuestionFilterService


@pytest.mark.django_db
def test_inclusion_preset_filters_to_selected_categories():
    culture = Category.objects.create(name="Culture")
    science = Category.objects.create(name="Science")
    sports = Category.objects.create(name="Sports")
    Question.objects.create(category=culture, text="Q1")
    Question.objects.create(category=science, text="Q2")
    Question.objects.create(category=sports, text="Q3")
    preset = ThemePreset.objects.create(name="Inclure", is_exclusion=False)
    preset.categories.set([culture, sports])

    queryset = ThemePresetQuestionFilterService(preset).filter_questions()

    ids = set(queryset.values_list("text", flat=True))
    assert ids == {"Q1", "Q3"}


@pytest.mark.django_db
def test_exclusion_preset_excludes_selected_categories():
    culture = Category.objects.create(name="Culture")
    science = Category.objects.create(name="Science")
    sports = Category.objects.create(name="Sports")
    Question.objects.create(category=culture, text="Q1")
    Question.objects.create(category=science, text="Q2")
    Question.objects.create(category=sports, text="Q3")
    preset = ThemePreset.objects.create(name="Exclure", is_exclusion=True)
    preset.categories.set([science])

    queryset = ThemePresetQuestionFilterService(preset).filter_questions()

    ids = set(queryset.values_list("text", flat=True))
    assert ids == {"Q1", "Q3"}


@pytest.mark.django_db
def test_inclusion_preset_without_categories_returns_none():
    culture = Category.objects.create(name="Culture")
    Question.objects.create(category=culture, text="Q1")
    preset = ThemePreset.objects.create(name="Vide", is_exclusion=False)

    queryset = ThemePresetQuestionFilterService(preset).filter_questions()

    assert queryset.count() == 0


@pytest.mark.django_db
def test_exclusion_preset_without_categories_returns_all():
    culture = Category.objects.create(name="Culture")
    Question.objects.create(category=culture, text="Q1")
    preset = ThemePreset.objects.create(name="Exclure vide", is_exclusion=True)

    queryset = ThemePresetQuestionFilterService(preset).filter_questions()

    assert queryset.count() == 1
