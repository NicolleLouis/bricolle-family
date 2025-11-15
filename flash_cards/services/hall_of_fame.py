from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from django.db.models import ExpressionWrapper, F, FloatField, QuerySet

from flash_cards.models import Question


@dataclass(frozen=True)
class HardQuestion:
    question: Question
    success_rate: float
    error_rate: float
    failure_count: int


class HallOfFameService:
    """Provide statistics about the hardest flash card questions."""

    def __init__(self, queryset: QuerySet | None = None) -> None:
        self._base_queryset = queryset or Question.objects.all()

    def get_hardest_questions(
        self, *, category_id: int | None = None, limit: int = 10
    ) -> Sequence[HardQuestion]:
        queryset = self._filtered_queryset(category_id)
        queryset = self._annotated_queryset(queryset)
        questions = queryset[:limit]
        return tuple(self._build_entry(question) for question in questions)

    def _filtered_queryset(
        self, category_id: int | None
    ) -> QuerySet:
        queryset = self._base_queryset.filter(answer_number__gt=0)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def _annotated_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.annotate(
            computed_error_rate=ExpressionWrapper(
                F("negative_answer_number") * 1.0 / F("answer_number"),
                output_field=FloatField(),
            ),
        ).order_by("-computed_error_rate", "text")

    def _build_entry(self, question: Question) -> HardQuestion:
        error_rate = getattr(question, "computed_error_rate", 0.0) or 0.0
        success_rate = max(0.0, min(1.0, 1.0 - error_rate))
        return HardQuestion(
            question=question,
            success_rate=success_rate,
            error_rate=error_rate,
            failure_count=question.negative_answer_number,
        )


__all__: Iterable[str] = ("HallOfFameService", "HardQuestion")
