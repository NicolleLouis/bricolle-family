from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from django.db import transaction

from flash_cards.models import Answer, Category, Question


class QuestionCreationError(ValueError):
    """Raised when question creation data is invalid."""


@dataclass
class QuestionPayload:
    text: str
    category: Category
    context: str | None
    positive_answers: Sequence[str]
    negative_answers: Sequence[str]


class QuestionCreationService:
    """Create questions with their answers from structured payloads."""

    def create_question(
        self,
        *,
        text: str,
        category_id: int | None = None,
        category_name: str | None = None,
        context: str | None = None,
        positive_answers: Iterable[str],
        negative_answers: Iterable[str],
    ) -> Question:
        payload = self._build_payload(
            text=text,
            category_id=category_id,
            category_name=category_name,
            context=context,
            positive_answers=positive_answers,
            negative_answers=negative_answers,
        )

        with transaction.atomic():
            question = Question.objects.create(
                category=payload.category,
                text=payload.text,
                explanation=payload.context,
            )
            answers = [
                Answer(question=question, text=answer_text, is_correct=True)
                for answer_text in payload.positive_answers
            ] + [
                Answer(question=question, text=answer_text, is_correct=False)
                for answer_text in payload.negative_answers
            ]
            Answer.objects.bulk_create(answers)
            return question

    def _build_payload(
        self,
        *,
        text: str,
        category_id: int | None,
        category_name: str | None,
        context: str | None,
        positive_answers: Iterable[str],
        negative_answers: Iterable[str],
    ) -> QuestionPayload:
        cleaned_text = (text or "").strip()
        if not cleaned_text:
            raise QuestionCreationError("Le champ 'question' est requis.")

        category = self._resolve_category(category_id=category_id, category_name=category_name)

        cleaned_positive = self._clean_answers(positive_answers)
        cleaned_negative = self._clean_answers(negative_answers)
        if not cleaned_positive:
            raise QuestionCreationError("Fournissez au moins une réponse positive.")
        if not cleaned_negative:
            raise QuestionCreationError("Fournissez au moins une réponse négative.")

        cleaned_context = (context or "").strip() or None

        return QuestionPayload(
            text=cleaned_text,
            category=category,
            context=cleaned_context,
            positive_answers=cleaned_positive,
            negative_answers=cleaned_negative,
        )

    def _resolve_category(
        self,
        *,
        category_id: int | None,
        category_name: str | None,
    ) -> Category:
        if category_id:
            return Category.objects.get(pk=category_id)
        cleaned_name = (category_name or "").strip()
        if not cleaned_name:
            raise QuestionCreationError(
                "Spécifiez 'category_id' ou 'category_name'."
            )
        category, _ = Category.objects.get_or_create(name=cleaned_name)
        return category

    @staticmethod
    def _clean_answers(answers: Iterable[str]) -> list[str]:
        return [answer.strip() for answer in answers if answer and answer.strip()]
