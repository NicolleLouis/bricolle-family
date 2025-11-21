import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from flash_cards.models import Category, Question, QuestionResult
from flash_cards.services import QuestionRetrievalService


@pytest.mark.django_db
def test_service_returns_random_question_when_only_random_strategy(monkeypatch):
    category = Category.objects.create(name="General")
    question = Question.objects.create(category=category, text="Capital of France ?")
    user = get_user_model().objects.create(username="player")

    service = QuestionRetrievalService(user=user)
    service._strategies = ((service._random_question, 1),)

    assert service.get_question() == question


@pytest.mark.django_db
def test_service_returns_last_failed_question(monkeypatch):
    category = Category.objects.create(name="History")
    user = get_user_model().objects.create(username="player")
    failing = Question.objects.create(category=category, text="Capital of Spain ?")
    QuestionResult.objects.create(
        user=user, question=failing, answer_number=1, last_answer_result=False
    )
    Question.objects.create(category=category, text="Capital of Italy ?")

    service = QuestionRetrievalService(user=user)
    service._strategies = ((service._last_failed_question, 1),)

    assert service.get_question() == failing


@pytest.mark.django_db
def test_service_falls_back_to_random_when_strategy_returns_none(monkeypatch):
    category = Category.objects.create(name="Science")
    question = Question.objects.create(category=category, text="Planet closest to sun ?")
    user = get_user_model().objects.create(username="player")

    service = QuestionRetrievalService(user=user)

    def empty_strategy():
        return None

    service._strategies = ((empty_strategy, 1),)

    assert service.get_question() == question


@pytest.mark.django_db
def test_service_least_answered_strategy():
    category = Category.objects.create(name="Geography")
    user = get_user_model().objects.create(username="player")
    q1 = Question.objects.create(category=category, text="Capital 1")
    least = Question.objects.create(category=category, text="Capital 2")
    q3 = Question.objects.create(category=category, text="Capital 3")
    QuestionResult.objects.create(user=user, question=q1, answer_number=5)
    QuestionResult.objects.create(user=user, question=q3, answer_number=2)

    service = QuestionRetrievalService(user=user)
    service._strategies = ((service._least_answered_question, 1),)

    assert service.get_question() == least


@pytest.mark.django_db
def test_service_oldest_last_answer_strategy():
    category = Category.objects.create(name="History")
    user = get_user_model().objects.create(username="player")
    recent = Question.objects.create(category=category, text="Recent")
    oldest = Question.objects.create(category=category, text="Oldest")
    never = Question.objects.create(category=category, text="Never")
    QuestionResult.objects.create(
        user=user, question=recent, last_answer=timezone.now(), answer_number=1
    )
    QuestionResult.objects.create(
        user=user,
        question=oldest,
        last_answer=timezone.now() - timedelta(days=5),
        answer_number=1,
    )

    service = QuestionRetrievalService(user=user)
    service._strategies = ((service._oldest_last_answer_question, 1),)

    assert service.get_question() == oldest


@pytest.mark.django_db
def test_service_high_error_strategy(monkeypatch):
    category = Category.objects.create(name="Math")
    user = get_user_model().objects.create(username="player")
    low = Question.objects.create(category=category, text="Easy")
    high = Question.objects.create(category=category, text="Hard")
    QuestionResult.objects.create(
        user=user, question=low, answer_number=10, negative_answer_number=1
    )
    QuestionResult.objects.create(
        user=user, question=high, answer_number=10, negative_answer_number=8
    )

    service = QuestionRetrievalService(user=user)
    service._strategies = ((service._high_error_question, 2),)

    monkeypatch.setattr("flash_cards.services.questions.random.random", lambda: 0.6)

    assert service.get_question() == high
