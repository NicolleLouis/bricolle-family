from __future__ import annotations

from typing import Iterable, Tuple

import plotly.express as px
from django.db.models import Count, ExpressionWrapper, FloatField, QuerySet, Sum
from django.db.models import F, Q

from flash_cards.models import Category, Question


class QuestionAttemptDistributionChartService:
    """Render a bar chart showing how many questions reached each attempt count."""

    def __init__(self, queryset: QuerySet[Question] | None = None) -> None:
        self._queryset = queryset or Question.objects.all()

    def render(self) -> str:
        buckets = self._attempt_distribution()
        if not buckets:
            return ""

        attempts = [bucket["answer_number"] for bucket in buckets]
        question_counts = [bucket["question_count"] for bucket in buckets]

        fig = px.line(
            x=attempts,
            y=question_counts,
            markers=True,
            labels={
                "x": "Nombre d'essais",
                "y": "Nombre de questions",
            },
            title="Répartition des questions par nombre d'essais",
        )
        fig.update_layout(margin=dict(t=60, b=0, l=0, r=0))
        fig.update_traces(line=dict(color="#0d6efd"), marker=dict(color="#0d6efd"))

        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def _attempt_distribution(self) -> list[dict[str, int]]:
        return list(
            self._queryset.values("answer_number")
            .order_by("answer_number")
            .annotate(question_count=Count("id"))
        )


class QuestionPerformanceScatterChartService:
    """Render a scatter plot with a linear regression trendline describing success rates."""

    def __init__(self, queryset: QuerySet[Question] | None = None) -> None:
        self._queryset = queryset or Question.objects.all()

    def render(self) -> Tuple[str, float | None]:
        points = self._performance_points()
        if len(points) < 2:
            return "", None

        attempts = [point["answer_number"] for point in points]
        success_rates = [point["success_rate"] * 100 for point in points]
        labels = [point["label"] for point in points]

        fig = px.scatter(
            x=attempts,
            y=success_rates,
            hover_name=labels,
            labels={
                "x": "Nombre d'essais",
                "y": "Taux de réussite (%)",
            },
            title="Taux de réussite par question",
        )
        fig.update_layout(margin=dict(t=60, b=0, l=0, r=0))

        slope, intercept, r_squared = self._compute_trendline(attempts, success_rates)
        accuracy = None
        if slope is not None and intercept is not None and r_squared is not None:
            line_x = [min(attempts), max(attempts)]
            line_y = [slope * value + intercept for value in line_x]
            fig.add_scatter(
                x=line_x,
                y=line_y,
                mode="lines",
                name="Tendance",
                line=dict(color="#dc3545"),
            )
            accuracy = round(r_squared * 100, 1)

        return fig.to_html(full_html=False, include_plotlyjs="cdn"), accuracy

    def _performance_points(self) -> list[dict[str, float]]:
        queryset = (
            self._queryset.filter(answer_number__gt=0)
            .annotate(
                success_rate=ExpressionWrapper(
                    F("positive_answer_number") * 1.0 / F("answer_number"),
                    output_field=FloatField(),
                )
            )
            .order_by("-answer_number")
        )
        points = []
        for question in queryset:
            text = getattr(question, "text", "")
            label = text[:60] + ("…" if len(text) > 60 else "")
            points.append(
                {
                    "answer_number": question.answer_number,
                    "success_rate": getattr(question, "success_rate", 0.0),
                    "label": label or f"Question #{question.id}",
                }
            )
        return points

    def _compute_trendline(self, x: Iterable[float], y: Iterable[float]) -> tuple[float | None, float | None, float | None]:
        x_values = list(x)
        y_values = list(y)
        n = len(x_values)
        if n < 2:
            return None, None, None

        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x_val * y_val for x_val, y_val in zip(x_values, y_values))
        sum_xx = sum(x_val * x_val for x_val in x_values)
        sum_yy = sum(y_val * y_val for y_val in y_values)

        denominator = n * sum_xx - sum_x * sum_x
        if denominator == 0:
            return None, None, None

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        # Calculate R-squared
        mean_y = sum_y / n
        ss_tot = sum((value - mean_y) ** 2 for value in y_values)
        ss_res = sum(
            (actual - (slope * x_val + intercept)) ** 2
            for x_val, actual in zip(x_values, y_values)
        )
        if ss_tot == 0:
            return slope, intercept, None

        r_squared = max(0.0, 1 - (ss_res / ss_tot))
        return slope, intercept, r_squared


class CategoryPerformanceLeaderboardService:
    """Return the best-performing categories based on success rate."""

    def __init__(self, queryset: QuerySet[Category] | None = None) -> None:
        self._queryset = queryset or Category.objects.all()

    def top_categories(self, limit: int = 5) -> list[dict[str, object]]:
        categories = (
            self._queryset.filter(questions__answer_number__gt=0)
            .annotate(
                total_answers=Sum("questions__answer_number"),
                total_positive=Sum("questions__positive_answer_number"),
                question_count=Count(
                    "questions",
                    filter=Q(questions__answer_number__gt=0),
                    distinct=True,
                ),
            )
            .exclude(total_answers__isnull=True)
            .annotate(
                success_rate=ExpressionWrapper(
                    F("total_positive") * 1.0 / F("total_answers"),
                    output_field=FloatField(),
                )
            )
            .order_by("-success_rate", "-total_answers", "-question_count", "name")
        )

        leaderboard = []
        for index, category in enumerate(categories[:limit]):
            rate = getattr(category, "success_rate", 0.0) or 0.0
            leaderboard.append(
                {
                    "name": category.name,
                    "success_rate": round(rate * 100, 1),
                    "question_count": category.question_count or 0,
                    "medal": self._medal_for_rank(index),
                }
            )
        return leaderboard

    def _medal_for_rank(self, index: int) -> str | None:
        if index == 0:
            return "gold"
        if index == 1:
            return "silver"
        if index == 2:
            return "bronze"
        return None
