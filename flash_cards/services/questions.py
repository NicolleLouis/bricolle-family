import random
from typing import Callable, Tuple

from django.db.models import (
    ExpressionWrapper,
    F,
    FloatField,
    IntegerField,
    OuterRef,
    Subquery,
    Value,
)
from django.db.models.functions import Coalesce, TruncDate

from flash_cards.models import Question, QuestionResult


Strategy = Callable[[], Question | None]


class QuestionRetrievalService:
    """Select a question using weighted strategies based on per-user stats when provided."""

    def __init__(self, queryset=None, user=None) -> None:
        self.user = user
        self._answer_field = "answer_number" if user is None else "user_answer_number"
        self._negative_field = (
            "negative_answer_number"
            if user is None
            else "user_negative_answer_number"
        )
        self._positive_field = (
            "positive_answer_number"
            if user is None
            else "user_positive_answer_number"
        )
        self._last_result_field = (
            "last_answer_result" if user is None else "user_last_answer_result"
        )
        self._last_answer_field = (
            "last_answer" if user is None else "user_last_answer"
        )

        base_queryset = queryset or Question.objects.all()
        self.queryset = (
            self._with_user_stats(base_queryset) if user else base_queryset
        )
        self._strategies: Tuple[Tuple[Strategy, int], ...] = (
            (self._random_question, 1),
            (self._last_failed_question, 3),
            (self._least_answered_question, 5),
            (self._oldest_last_answer_question, 2),
            (self._high_error_question, 3),
        )

    def get_question(self) -> Question | None:
        strategy = self._pick_strategy()
        question = strategy()
        if question:
            return question
        return self._random_question()

    def _pick_strategy(self) -> Strategy:
        total_weight = sum(weight for _, weight in self._strategies)
        threshold = random.uniform(0, total_weight)
        cumulative = 0.0
        for strategy, weight in self._strategies:
            cumulative += weight
            if threshold <= cumulative:
                return strategy
        return self._strategies[-1][0]

    def _random_question(self) -> Question | None:
        return self.queryset.order_by("?").first()

    def _last_failed_question(self) -> Question | None:
        conditions = {f"{self._answer_field}__gt": 0, self._last_result_field: False}
        return self.queryset.filter(**conditions).order_by("?").first()

    def _least_answered_question(self) -> Question | None:
        if self.user:
            unseen = self.queryset.filter(user_answer_number__isnull=True)
            if unseen.exists():
                return unseen.order_by("?").first()
        return self.queryset.order_by(self._answer_field, "?").first()

    def _oldest_last_answer_question(self) -> Question | None:
        queryset = self.queryset.exclude(**{f"{self._last_answer_field}__isnull": True}).annotate(
            last_answer_day=TruncDate(self._last_answer_field)
        )
        return queryset.order_by("last_answer_day", "?").first()

    def _high_error_question(self) -> Question | None:
        threshold = random.random()
        queryset = (
            self.queryset.filter(**{f"{self._answer_field}__gt": 0})
            .annotate(
                calculated_error=ExpressionWrapper(
                    F(self._negative_field) * 1.0 / F(self._answer_field),
                    output_field=FloatField(),
                )
            )
            .filter(calculated_error__gte=threshold)
        )
        return queryset.order_by("?").first()

    def _with_user_stats(self, queryset):
        if not self.user:
            return queryset
        result_subquery = QuestionResult.objects.filter(
            user=self.user, question=OuterRef("pk")
        )
        return queryset.annotate(
            user_answer_number=Subquery(
                result_subquery.values("answer_number")[:1], output_field=IntegerField()
            ),
            user_positive_answer_number=Coalesce(
                Subquery(result_subquery.values("positive_answer_number")[:1]),
                Value(0),
            ),
            user_negative_answer_number=Coalesce(
                Subquery(result_subquery.values("negative_answer_number")[:1]),
                Value(0),
            ),
            user_last_answer_result=Coalesce(
                Subquery(result_subquery.values("last_answer_result")[:1]), Value(False)
            ),
            user_last_answer=Subquery(result_subquery.values("last_answer")[:1]),
        )
