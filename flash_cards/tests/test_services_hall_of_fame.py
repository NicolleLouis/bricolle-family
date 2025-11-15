import pytest

from flash_cards.models import Category, Question
from flash_cards.services import HallOfFameService


@pytest.mark.django_db
def test_hall_of_fame_service_orders_questions_by_error_rate():
    category = Category.objects.create(name="Culture")
    hardest = Question.objects.create(
        category=category,
        text="Question difficile",
        answer_number=10,
        positive_answer_number=2,
        negative_answer_number=8,
    )
    easier = Question.objects.create(
        category=category,
        text="Question plus simple",
        answer_number=10,
        positive_answer_number=5,
        negative_answer_number=5,
    )
    Question.objects.create(
        category=category,
        text="Ignorée car aucune réponse",
        answer_number=0,
        positive_answer_number=0,
        negative_answer_number=0,
    )

    service = HallOfFameService()

    entries = service.get_hardest_questions()

    assert [entry.question for entry in entries] == [hardest, easier]
    assert entries[0].failure_count == 8
    assert entries[0].success_rate == pytest.approx(0.2)


@pytest.mark.django_db
def test_hall_of_fame_service_filters_by_category_and_limits_results():
    culture = Category.objects.create(name="Culture")
    science = Category.objects.create(name="Science")
    for index in range(12):
        Question.objects.create(
            category=culture,
            text=f"Culture #{index}",
            answer_number=100,
            positive_answer_number=100 - index,
            negative_answer_number=index,
        )
    Question.objects.create(
        category=science,
        text="Science devrait être filtré",
        answer_number=10,
        positive_answer_number=8,
        negative_answer_number=2,
    )

    service = HallOfFameService()

    entries = service.get_hardest_questions(category_id=culture.id)

    assert len(entries) == 10
    assert all(entry.question.category_id == culture.id for entry in entries)
    assert all(entry.failure_count >= entries[-1].failure_count for entry in entries[:-1])
