import pytest

from flash_cards.models import Answer, Category, Question
from flash_cards.services import QuestionUpdateError, QuestionUpdateService


@pytest.mark.django_db
def test_update_question_updates_fields_and_resets_needs_rework():
    category = Category.objects.create(name="Culture")
    question = Question.objects.create(
        category=category,
        text="Capital of Italy ?",
        explanation="Europe",
        needs_rework=True,
    )
    Answer.objects.create(question=question, text="Rome", is_correct=True)
    Answer.objects.create(question=question, text="Milan", is_correct=False)

    service = QuestionUpdateService()
    updated = service.update_question(
        question=question,
        text="Capitale de l'Italie ?",
        category_name="Geographie",
        context="Chapitre Europe",
        positive_answers=["Rome"],
        negative_answers=["Venise"],
        update_context=True,
        update_answers=True,
    )

    assert updated.needs_rework is False
    assert updated.text == "Capitale de l'Italie ?"
    assert updated.category.name == "Geographie"
    assert updated.explanation == "Chapitre Europe"
    assert list(updated.answers.filter(is_correct=True).values_list("text", flat=True)) == [
        "Rome"
    ]
    assert list(updated.answers.filter(is_correct=False).values_list("text", flat=True)) == [
        "Venise"
    ]


@pytest.mark.django_db
def test_update_question_rejects_empty_text():
    category = Category.objects.create(name="Culture")
    question = Question.objects.create(category=category, text="Capital ?")

    service = QuestionUpdateService()

    with pytest.raises(QuestionUpdateError):
        service.update_question(question=question, text="   ")


@pytest.mark.django_db
def test_update_question_requires_answers_when_updating():
    category = Category.objects.create(name="Culture")
    question = Question.objects.create(category=category, text="Capital ?")

    service = QuestionUpdateService()

    with pytest.raises(QuestionUpdateError):
        service.update_question(
            question=question,
            positive_answers=["Paris"],
            negative_answers=[],
            update_answers=True,
        )
