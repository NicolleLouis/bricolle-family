import pytest

from flash_cards.models import Answer, Category, Question


@pytest.mark.django_db
def test_category_str_returns_name():
    category = Category.objects.create(name="Vocabulary")

    assert str(category) == "Vocabulary"


@pytest.mark.django_db
def test_question_defaults():
    category = Category.objects.create(name="Geography")

    question = Question.objects.create(category=category, text="Capital of France?")

    assert question.answer_number == 0
    assert question.positive_answer_number == 0
    assert question.negative_answer_number == 0
    assert question.last_answer is None
    assert question.last_answer_result is False
    assert question.is_valid is False
    assert question.error_rate == 0.0

    Answer.objects.create(question=question, text="Paris", is_correct=True)
    Answer.objects.create(question=question, text="London", is_correct=False)
    assert question.is_valid is True
    question.answer_number = 2
    question.negative_answer_number = 1
    assert question.error_rate == 0.5


@pytest.mark.django_db
def test_answer_defaults():
    category = Category.objects.create(name="Math")
    question = Question.objects.create(category=category, text="2 + 2 ?")

    answer = Answer.objects.create(question=question, text="4")

    assert answer.is_correct is False
    assert str(answer) == "4"
