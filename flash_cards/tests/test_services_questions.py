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
def test_strategy_picker_respects_weights(monkeypatch):
    user = get_user_model().objects.create(username="player")
    service = QuestionRetrievalService(user=user)
    s1 = lambda: "first"
    s2 = lambda: "second"
    s3 = lambda: "third"
    service._strategies = ((s1, 1), (s2, 3), (s3, 6))

    thresholds = iter([0.0, 0.9, 1.01, 3.5, 4.1, 9.9])
    monkeypatch.setattr(
        "flash_cards.services.questions.random.uniform",
        lambda low, high: next(thresholds),
    )

    assert [service._pick_strategy() for _ in range(6)] == [s1, s1, s2, s2, s3, s3]


def test_service_requires_user():
    with pytest.raises(ValueError):
        QuestionRetrievalService()


@pytest.mark.django_db
def test_service_returns_last_failed_question(monkeypatch):
    category = Category.objects.create(name="History")
    user = get_user_model().objects.create(username="player")
    failing = Question.objects.create(category=category, text="Capital of Spain ?")
    QuestionResult.objects.create(
        user=user, question=failing, answer_number=1, last_answer_result=False
    )
    successful = Question.objects.create(category=category, text="Capital of Italy ?")
    QuestionResult.objects.create(
        user=user, question=successful, answer_number=1, last_answer_result=True
    )

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
def test_service_prefers_unanswered_when_least_strategy_selected(monkeypatch):
    category = Category.objects.create(name="Geography")
    user = get_user_model().objects.create(username="player")
    answered = Question.objects.create(category=category, text="Seen capital")
    unseen = Question.objects.create(category=category, text="New capital")
    QuestionResult.objects.create(user=user, question=answered, answer_number=3)

    # Force the weighted picker into the _least_answered_question range.
    monkeypatch.setattr(
        "flash_cards.services.questions.random.uniform",
        lambda low, high: 4.5,
    )

    service = QuestionRetrievalService(user=user)

    assert service.get_question() == unseen


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
    QuestionResult.objects.create(user=user, question=never, answer_number=0)

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
