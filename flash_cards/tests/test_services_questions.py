import pytest
from datetime import timedelta
from django.utils import timezone

from flash_cards.models import Category, Question
from flash_cards.services import QuestionRetrievalService


@pytest.mark.django_db
def test_service_returns_random_question_when_only_random_strategy(monkeypatch):
    category = Category.objects.create(name="General")
    question = Question.objects.create(category=category, text="Capital of France ?")

    service = QuestionRetrievalService()
    service._strategies = ((service._random_question, 1),)

    assert service.get_question() == question


@pytest.mark.django_db
def test_service_returns_last_failed_question(monkeypatch):
    category = Category.objects.create(name="History")
    failing = Question.objects.create(
        category=category,
        text="Capital of Spain ?",
        answer_number=1,
        last_answer_result=False,
    )
    Question.objects.create(category=category, text="Capital of Italy ?")

    service = QuestionRetrievalService()
    service._strategies = ((service._last_failed_question, 1),)

    assert service.get_question() == failing


@pytest.mark.django_db
def test_service_falls_back_to_random_when_strategy_returns_none(monkeypatch):
    category = Category.objects.create(name="Science")
    question = Question.objects.create(category=category, text="Planet closest to sun ?")

    service = QuestionRetrievalService()

    def empty_strategy():
        return None

    service._strategies = ((empty_strategy, 1),)

    assert service.get_question() == question


@pytest.mark.django_db
def test_service_least_answered_strategy():
    category = Category.objects.create(name="Geography")
    Question.objects.create(category=category, text="Capital 1", answer_number=5)
    least = Question.objects.create(category=category, text="Capital 2", answer_number=0)
    Question.objects.create(category=category, text="Capital 3", answer_number=2)

    service = QuestionRetrievalService()
    service._strategies = ((service._least_answered_question, 1),)

    assert service.get_question() == least


@pytest.mark.django_db
def test_service_oldest_last_answer_strategy():
    category = Category.objects.create(name="History")
    Question.objects.create(
        category=category, text="Recent", last_answer=timezone.now()
    )
    oldest = Question.objects.create(
        category=category,
        text="Oldest",
        last_answer=timezone.now() - timedelta(days=5),
    )
    Question.objects.create(category=category, text="Never")

    service = QuestionRetrievalService()
    service._strategies = ((service._oldest_last_answer_question, 1),)

    assert service.get_question() == oldest


@pytest.mark.django_db
def test_service_high_error_strategy(monkeypatch):
    category = Category.objects.create(name="Math")
    low = Question.objects.create(
        category=category, text="Easy", answer_number=10, negative_answer_number=1
    )
    high = Question.objects.create(
        category=category, text="Hard", answer_number=10, negative_answer_number=8
    )

    service = QuestionRetrievalService()
    service._strategies = ((service._high_error_question, 2),)

    monkeypatch.setattr("flash_cards.services.questions.random.random", lambda: 0.6)

    assert service.get_question() == high
