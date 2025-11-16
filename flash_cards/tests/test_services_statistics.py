from unittest.mock import MagicMock, patch

import pytest

from flash_cards.models import Category, Question
from flash_cards.services.statistics import (
    CategoryPerformanceLeaderboardService,
    QuestionAttemptDistributionChartService,
    QuestionPerformanceScatterChartService,
)


@pytest.mark.django_db
@patch("flash_cards.services.statistics.px")
def test_render_builds_attempt_distribution_chart(mock_px):
    mock_fig = MagicMock()
    mock_fig.to_html.return_value = "<div>chart</div>"
    mock_px.line.return_value = mock_fig

    category = Category.objects.create(name="Culture")
    Question.objects.create(category=category, text="Question 1", answer_number=0)
    Question.objects.create(category=category, text="Question 2", answer_number=2)
    Question.objects.create(category=category, text="Question 3", answer_number=2)

    html = QuestionAttemptDistributionChartService().render()

    assert html == "<div>chart</div>"
    _, kwargs = mock_px.line.call_args
    assert kwargs["x"] == [0, 2]
    assert kwargs["y"] == [1, 2]
    assert kwargs["title"] == "Répartition des questions par nombre d'essais"


@pytest.mark.django_db
@patch("flash_cards.services.statistics.px")
def test_render_returns_empty_string_without_data(mock_px):
    html = QuestionAttemptDistributionChartService().render()

    assert html == ""
    mock_px.line.assert_not_called()


@pytest.mark.django_db
@patch("flash_cards.services.statistics.px")
def test_performance_scatter_renders_chart_and_accuracy(mock_px):
    mock_fig = MagicMock()
    mock_fig.to_html.return_value = "<div>scatter</div>"
    mock_px.scatter.return_value = mock_fig

    category = Category.objects.create(name="Culture")
    Question.objects.create(
        category=category,
        text="Question 1",
        answer_number=2,
        positive_answer_number=1,
    )
    Question.objects.create(
        category=category,
        text="Question 2",
        answer_number=4,
        positive_answer_number=3,
    )

    html, accuracy = QuestionPerformanceScatterChartService().render()

    assert html == "<div>scatter</div>"
    assert accuracy == pytest.approx(100.0)
    mock_fig.add_scatter.assert_called_once()


@pytest.mark.django_db
@patch("flash_cards.services.statistics.px")
def test_performance_scatter_requires_enough_points(mock_px):
    category = Category.objects.create(name="Culture")
    Question.objects.create(
        category=category,
        text="Question 1",
        answer_number=1,
        positive_answer_number=1,
    )

    html, accuracy = QuestionPerformanceScatterChartService().render()

    assert html == ""
    assert accuracy is None
    mock_px.scatter.assert_not_called()


@pytest.mark.django_db
def test_category_leaderboard_returns_top_entries():
    culture = Category.objects.create(name="Culture")
    math = Category.objects.create(name="Maths")
    geo = Category.objects.create(name="Geo")
    history = Category.objects.create(name="Histoire")
    science = Category.objects.create(name="Science")
    extra = Category.objects.create(name="Bonus")

    Question.objects.create(
        category=culture,
        text="Q1",
        answer_number=4,
        positive_answer_number=3,
    )
    Question.objects.create(
        category=math,
        text="Q2",
        answer_number=2,
        positive_answer_number=2,
    )
    Question.objects.create(
        category=geo,
        text="Q3",
        answer_number=3,
        positive_answer_number=1,
    )
    Question.objects.create(
        category=history,
        text="Q4",
        answer_number=10,
        positive_answer_number=7,
    )
    Question.objects.create(
        category=science,
        text="Q5",
        answer_number=5,
        positive_answer_number=5,
    )
    Question.objects.create(
        category=extra,
        text="Q6",
        answer_number=1,
        positive_answer_number=1,
    )

    data = CategoryPerformanceLeaderboardService().top_categories()

    assert len(data) == 5
    assert data[0]["name"] in {"Maths", "Science"}
    assert data[0]["medal"] == "gold"
    assert data[1]["medal"] == "silver"
    assert data[2]["medal"] == "bronze"
    assert all(entry["success_rate"] >= data[index + 1]["success_rate"] for index, entry in enumerate(data[:-1]))
