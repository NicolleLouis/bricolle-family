import importlib
import json

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
def test_question_creation_from_json(client, user):
    category = Category.objects.create(name="Culture")
    client.force_login(user)

    response = client.post(
        reverse("flash_cards:question_create_json"),
        {
            "payload": json.dumps(
                {
                    "category_id": category.id,
                    "question": "Quelle est la capitale de l'Allemagne ?",
                    "context": "Chapitre Europe",
                    "positive_answers": ["Berlin"],
                    "negative_answers": ["Munich"],
                }
            )
        },
    )

    assert response.status_code == 302
    question = Question.objects.get()
    assert question.text.startswith("Quelle est la capitale de l'Allemagne")


@pytest.mark.django_db
def test_question_creation_from_json_batch(client, user):
    category = Category.objects.create(name="Culture")
    client.force_login(user)

    response = client.post(
        reverse("flash_cards:question_create_json"),
        {
            "payload": json.dumps(
                [
                    {
                        "category_id": category.id,
                        "question": "Quel fleuve traverse Paris ?",
                        "context": "Géographie",
                        "positive_answers": ["La Seine"],
                        "negative_answers": ["Le Rhône"],
                    },
                    {
                        "category": "Sciences",
                        "question": "Quelle molécule compose l'eau ?",
                        "context": "Chimie",
                        "positive_answers": ["H2O"],
                        "negative_answers": ["CO2"],
                    },
                ]
            )
        },
    )

    assert response.status_code == 302
    assert Question.objects.count() == 2
    assert Category.objects.filter(name="Sciences").exists()


@pytest.mark.django_db
def test_question_creation_from_json_invalid_payload(client, user):
    client.force_login(user)

    response = client.post(
        reverse("flash_cards:question_create_json"),
        {
            "payload": "{invalid json]",
        },
    )

    assert response.status_code == 200
    assert b"JSON invalide" in response.content
    assert Question.objects.count() == 0


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
def test_api_create_question(client, user):
    category = Category.objects.create(name="Sciences")
    client.force_login(user)

    response = client.post(
        reverse("flash_cards:api_question_create"),
        data=json.dumps(
            {
                "category_id": category.id,
                "question": "Quelle planète est la plus proche du soleil ?",
                "context": "Chapitre 1",
                "positive_answers": ["Mercure"],
                "negative_answers": ["Venus", "Terre"],
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["category"]["name"] == "Sciences"
    assert payload["question"].startswith("Quelle planète")
    assert payload["positive_answers"] == ["Mercure"]
    assert Question.objects.count() == 1


@pytest.mark.django_db
def test_api_create_question_accepts_array(client, user):
    category = Category.objects.create(name="Sciences")
    client.force_login(user)

    response = client.post(
        reverse("flash_cards:api_question_create"),
        data=json.dumps(
            [
                {
                    "category_id": category.id,
                    "question": "Capital du Canada ?",
                    "context": "Géo",
                    "positive_answers": ["Ottawa"],
                    "negative_answers": ["Toronto"],
                },
                {
                    "category": "Sports",
                    "question": "Combien de joueurs dans une équipe de basket ?",
                    "context": None,
                    "positive_answers": ["5"],
                    "negative_answers": ["6"],
                },
            ]
        ),
        content_type="application/json",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["count"] == 2
    assert len(payload["created"]) == 2
    assert any(item["category"]["name"] == "Sports" for item in payload["created"])
    assert Question.objects.count() == 2


@pytest.mark.django_db
def test_api_create_question_creates_category_from_name(client, user):
    client.force_login(user)

    response = client.post(
        reverse("flash_cards:api_question_create"),
        data=json.dumps(
            {
                "category": "Nouvelles catégories",
                "question": "Capital de l'Italie ?",
                "context": None,
                "positive_answers": ["Rome"],
                "negative_answers": ["Milan"],
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 201
    assert Category.objects.filter(name="Nouvelles catégories").exists()


@pytest.mark.django_db
def test_api_create_question_with_token(client, settings):
    settings.FLASH_CARDS_MCP_TOKEN = "secret"

    response = client.post(
        reverse("flash_cards:api_question_create"),
        data=json.dumps(
            {
                "category": "Animaux",
                "question": "Quel animal miaule ?",
                "context": "niveau 1",
                "positive_answers": ["Chat"],
                "negative_answers": ["Chien"],
            }
        ),
        content_type="application/json",
        HTTP_X_MCP_TOKEN="secret",
    )

    assert response.status_code == 201
    assert Question.objects.count() == 1


@pytest.mark.django_db
def test_api_create_question_validates_payload(client, user):
    client.force_login(user)

    response = client.post(
        reverse("flash_cards:api_question_create"),
        data=json.dumps(
            {
                "category": "",
                "question": "",
                "positive_answers": [],
                "negative_answers": [],
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.django_db
def test_api_list_categories(client, user):
    cat = Category.objects.create(name="Culture")
    other = Category.objects.create(name="Maths")
    Question.objects.create(category=cat, text="Capital de la France ?")
    client.force_login(user)

    response = client.get(reverse("flash_cards:api_categories"))

    assert response.status_code == 200
    data = response.json()["categories"]
    assert len(data) == 2
    culture_entry = next(item for item in data if item["name"] == "Culture")
    assert culture_entry["question_count"] == 1


@pytest.mark.django_db
def test_api_list_categories_requires_auth(client):
    response = client.get(reverse("flash_cards:api_categories"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_api_list_categories_accepts_token(client, settings):
    settings.FLASH_CARDS_MCP_TOKEN = "super-token"
    Category.objects.create(name="Culture")

    response = client.get(
        reverse("flash_cards:api_categories"),
        HTTP_X_MCP_TOKEN="super-token",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_api_categories_rejects_wrong_token(client, settings):
    settings.FLASH_CARDS_MCP_TOKEN = "expected"

    response = client.get(
        reverse("flash_cards:api_categories"),
        HTTP_X_MCP_TOKEN="other",
    )

    assert response.status_code == 403


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


@pytest.mark.django_db
def test_hall_of_fame_view_lists_questions(client, user):
    category = Category.objects.create(name="Culture")
    Question.objects.create(
        category=category,
        text="Quelle est la capitale de la France ?",
        answer_number=10,
        positive_answer_number=2,
        negative_answer_number=8,
    )

    client.force_login(user)
    response = client.get(reverse("flash_cards:hall_of_fame"))

    assert response.status_code == 200
    assert b"Hall Of Fame" in response.content
    assert b"capitale de la France" in response.content


@pytest.mark.django_db
def test_hall_of_fame_view_filters_by_category(client, user):
    culture = Category.objects.create(name="Culture")
    science = Category.objects.create(name="Science")
    Question.objects.create(
        category=culture,
        text="Question culture",
        answer_number=10,
        positive_answer_number=2,
        negative_answer_number=8,
    )
    Question.objects.create(
        category=science,
        text="Question science",
        answer_number=10,
        positive_answer_number=5,
        negative_answer_number=5,
    )

    client.force_login(user)
    response = client.get(
        reverse("flash_cards:hall_of_fame"), {"category": str(culture.id)}
    )

    assert response.status_code == 200
    assert b"Question culture" in response.content
    assert b"Question science" not in response.content


@pytest.mark.django_db
def test_statistics_view_renders_chart(client, user, monkeypatch):
    class DummyService:
        def render(self_inner):
            return "<div>chart</div>"

    class DummyPerformanceService:
        def render(self_inner):
            return "<div>scatter</div>", 87.5

    class DummyLeaderboardService:
        def top_categories(self_inner):
            return [
                {"name": "Culture", "success_rate": 80.0, "question_count": 5, "medal": "gold"}
            ]

    stats_module = importlib.import_module("flash_cards.views.statistics")
    monkeypatch.setattr(
        stats_module,
        "QuestionAttemptDistributionChartService",
        lambda: DummyService(),
    )
    monkeypatch.setattr(
        stats_module,
        "QuestionPerformanceScatterChartService",
        lambda: DummyPerformanceService(),
    )
    monkeypatch.setattr(
        stats_module,
        "CategoryPerformanceLeaderboardService",
        lambda: DummyLeaderboardService(),
    )

    client.force_login(user)
    response = client.get(reverse("flash_cards:statistics"))

    assert response.status_code == 200
    assert response.context["attempt_distribution_chart"] == "<div>chart</div>"
    assert response.context["performance_chart"] == "<div>scatter</div>"
    assert response.context["performance_trend_accuracy"] == 87.5
    assert response.context["category_leaderboard"][0]["name"] == "Culture"
    assert b"Statistiques" in response.content
