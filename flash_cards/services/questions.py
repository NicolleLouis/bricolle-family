import random
from typing import Callable, Tuple

from django.db.models import ExpressionWrapper, F, FloatField
from django.db.models.functions import TruncDate

from flash_cards.models import Question


Strategy = Callable[[], Question | None]


class QuestionRetrievalService:
    """Select a question using weighted strategies."""

    def __init__(self, queryset=None) -> None:
        self.queryset = queryset or Question.objects.all()
        self._strategies: Tuple[Tuple[Strategy, int], ...] = (
            (self._random_question, 1),
            (self._last_failed_question, 3),
            (self._least_answered_question, 2),
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
        return (
            self.queryset.filter(answer_number__gt=0, last_answer_result=False)
            .order_by("?")
            .first()
        )

    def _least_answered_question(self) -> Question | None:
        return (
            self.queryset.order_by("answer_number", "?").first()
        )

    def _oldest_last_answer_question(self) -> Question | None:
        queryset = self.queryset.exclude(last_answer__isnull=True).annotate(
            last_answer_day=TruncDate("last_answer")
        )
        return queryset.order_by("last_answer_day", "?").first()

    def _high_error_question(self) -> Question | None:
        threshold = random.random()
        queryset = (
            self.queryset.filter(answer_number__gt=0)
            .annotate(
                calculated_error=ExpressionWrapper(
                    F("negative_answer_number") * 1.0 / F("answer_number"),
                    output_field=FloatField(),
                )
            )
            .filter(calculated_error__gte=threshold)
        )
        return queryset.order_by("?").first()
