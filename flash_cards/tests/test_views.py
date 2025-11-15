import importlib

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from flash_cards.models import Answer, Category, Question


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="flash-user",
        password="password",
        is_staff=True,
    )


@pytest.mark.django_db
def test_settings_view_lists_questions(client, user):
    category = Category.objects.create(name="Culture")
    question1 = Question.objects.create(category=category, text="Capital of France ?")
    question2 = Question.objects.create(category=category, text="Capital of Spain ?")
    Answer.objects.create(question=question1, text="Paris", is_correct=True)

    client.force_login(user)
    response = client.get(reverse("flash_cards:settings"))

    assert response.status_code == 200
    content = response.content
    assert b"Capital of France" in content
    assert b"Capital of Spain" in content


@pytest.mark.django_db
def test_question_creation_flow(client, user):
    category = Category.objects.create(name="Math")
    client.force_login(user)

    url = reverse("flash_cards:question_create")
    data = {
        "category": category.id,
        "text": "2 + 2 ?",
        "answers-TOTAL_FORMS": "2",
        "answers-INITIAL_FORMS": "0",
        "answers-MIN_NUM_FORMS": "0",
        "answers-MAX_NUM_FORMS": "1000",
        "answers-0-text": "4",
        "answers-0-is_correct": "on",
        "answers-1-text": "5",
        "answers-1-is_correct": "",
    }

    response = client.post(url, data)

    assert response.status_code == 302
    question = Question.objects.get()
    answers = question.answers.all()
    assert question.text == "2 + 2 ?"
    assert answers.count() == 2
    assert answers.filter(is_correct=True).count() == 1


@pytest.mark.django_db
def test_delete_question(client, user):
    category = Category.objects.create(name="Geo")
    question = Question.objects.create(category=category, text="Capital of Spain ?")
    client.force_login(user)

    url = reverse("flash_cards:question_delete", args=[question.id])
    response = client.post(url)

    assert response.status_code == 302
    assert Question.objects.count() == 0


@pytest.mark.django_db
def test_settings_filter_questions(client, user):
    category = Category.objects.create(name="Geo")
    other_category = Category.objects.create(name="Culture")
    valid_question = Question.objects.create(category=category, text="Capital of France ?")
    invalid_question = Question.objects.create(category=other_category, text="Capital of Spain ?")
    Answer.objects.create(question=valid_question, text="Paris", is_correct=True)
    Answer.objects.create(question=valid_question, text="London", is_correct=False)
    Answer.objects.create(question=invalid_question, text="Madrid", is_correct=True)
    client.force_login(user)

    response = client.get(reverse("flash_cards:settings"), {"q": "France"})

    assert response.status_code == 200
    content = response.content
    assert b"Capital of France" in content
    assert b"Capital of Spain" not in content

    category_response = client.get(
        reverse("flash_cards:settings"), {"category": str(other_category.id)}
    )
    assert category_response.status_code == 200
    category_content = category_response.content
    assert b"Capital of Spain" in category_content
    assert b"Capital of France" not in category_content

    invalid_response = client.get(
        reverse("flash_cards:settings"), {"validity": "invalid"}
    )
    assert invalid_response.status_code == 200
    invalid_content = invalid_response.content
    assert b"Capital of Spain" in invalid_content
    assert b"Capital of France" not in invalid_content

    valid_response = client.get(
        reverse("flash_cards:settings"), {"validity": "valid"}
    )
    assert valid_response.status_code == 200
    valid_content = valid_response.content
    assert b"Capital of France" in valid_content
    assert b"Capital of Spain" not in valid_content


@pytest.mark.django_db
def test_categories_list_and_create(client, user):
    Category.objects.create(name="Culture")
    Category.objects.create(name="Math")
    client.force_login(user)

    list_response = client.get(reverse("flash_cards:categories"))
    assert list_response.status_code == 200
    assert b"Culture" in list_response.content
    assert b"Math" in list_response.content

    create_response = client.post(
        reverse("flash_cards:categories"),
        {"name": "Science"},
        follow=True,
    )
    assert create_response.status_code == 200
    assert Category.objects.filter(name="Science").exists()


@pytest.mark.django_db
def test_home_displays_question(client, user, monkeypatch):
    category = Category.objects.create(name="Trivia")
    question = Question.objects.create(category=category, text="Capital of France ?")
    Answer.objects.create(question=question, text="Paris", is_correct=True)
    Answer.objects.create(question=question, text="London", is_correct=False)

    class DummyService:
        def get_question(self_inner):
            return question

    home_module = importlib.import_module("flash_cards.views.home")
    monkeypatch.setattr(home_module, "QuestionRetrievalService", lambda: DummyService())

    client.force_login(user)
    response = client.get(reverse("flash_cards:home"))

    assert response.status_code == 200
    assert b"Capital of France" in response.content


@pytest.mark.django_db
def test_home_records_answer(client, user, monkeypatch):
    category = Category.objects.create(name="Science")
    question = Question.objects.create(category=category, text="Planet closest to the sun ?")
    correct = Answer.objects.create(question=question, text="Mercure", is_correct=True)
    wrong = Answer.objects.create(question=question, text="Mars", is_correct=False)

    class DummyService:
        def get_question(self_inner):
            return question

    home_module = importlib.import_module("flash_cards.views.home")
    monkeypatch.setattr(home_module, "QuestionRetrievalService", lambda: DummyService())

    client.force_login(user)
    response = client.post(
        reverse("flash_cards:home"),
        {
            "action": "answer",
            "question_id": question.id,
            "answers_order": f"{correct.id},{wrong.id}",
            "answer_id": str(correct.id),
        },
    )

    question.refresh_from_db()
    assert response.status_code == 200
    assert question.answer_number == 1
    assert question.positive_answer_number == 1
    assert question.negative_answer_number == 0
    assert question.last_answer_result is True
    assert b"Bonne r" in response.content


@pytest.mark.django_db
def test_home_limits_negatives_when_less_than_three(client, user, monkeypatch):
    category = Category.objects.create(name="Animals")
    question = Question.objects.create(category=category, text="Quel animal miaule ?")
    Answer.objects.create(question=question, text="Chat", is_correct=True)
    Answer.objects.create(question=question, text="Chien", is_correct=False)
    Answer.objects.create(question=question, text="Ours", is_correct=False)

    class DummyService:
        def get_question(self_inner):
            return question

    home_module = importlib.import_module("flash_cards.views.home")
    monkeypatch.setattr(home_module, "QuestionRetrievalService", lambda: DummyService())

    client.force_login(user)
    response = client.get(reverse("flash_cards:home"))

    context = response.context[-1]
    assert len(context["answers"]) == 2
