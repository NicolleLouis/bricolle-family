import pytest

from flash_cards.models import Category
from flash_cards.services import QuestionCreationError, QuestionCreationService


@pytest.mark.django_db
def test_question_creation_service_creates_question_and_answers():
    category = Category.objects.create(name="Science")
    service = QuestionCreationService()

    question = service.create_question(
        text="  Quelle est la planète la plus proche du soleil ?  ",
        category_id=category.id,
        context="Cours d'astronomie",
        positive_answers=["Mercure", " mercure "],
        negative_answers=["Mars", "", "Venus"],
    )

    assert question.text.startswith("Quelle est la planète")
    assert question.explanation == "Cours d'astronomie"
    assert question.answers.filter(is_correct=True).count() == 2
    assert question.answers.filter(is_correct=False).count() == 2


@pytest.mark.django_db
def test_question_creation_service_creates_category_if_needed():
    service = QuestionCreationService()

    question = service.create_question(
        text="Capital de la France ?",
        category_name="Géographie",
        context=None,
        positive_answers=["Paris"],
        negative_answers=["Lyon"],
    )

    assert question.category.name == "Géographie"
    assert Category.objects.filter(name="Géographie").exists()


@pytest.mark.django_db
def test_question_creation_service_requires_both_answer_types():
    service = QuestionCreationService()

    with pytest.raises(QuestionCreationError):
        service.create_question(
            text="Question incomplète ?",
            category_name="Divers",
            context="",
            positive_answers=["Oui"],
            negative_answers=[],
        )
