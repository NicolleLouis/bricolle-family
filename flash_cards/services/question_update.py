from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from django.db import transaction

from flash_cards.models import Answer, Category, Question


class QuestionUpdateError(ValueError):
    """Raised when question update data is invalid."""


@dataclass
class QuestionUpdatePayload:
    text: str | None
    category: Category | None
    context: str | None
    update_context: bool
    positive_answers: Sequence[str]
    negative_answers: Sequence[str]
    update_answers: bool


class QuestionUpdateService:
    """Update questions and their answers from structured payloads."""

    def update_question(
        self,
        *,
        question: Question,
        text: str | None = None,
        category_id: int | None = None,
        category_name: str | None = None,
        context: str | None = None,
        positive_answers: Iterable[str] | None = None,
        negative_answers: Iterable[str] | None = None,
        update_context: bool = False,
        update_answers: bool = False,
    ) -> Question:
        payload = self._build_payload(
            text=text,
            category_id=category_id,
            category_name=category_name,
            context=context,
            positive_answers=positive_answers,
            negative_answers=negative_answers,
            update_context=update_context,
            update_answers=update_answers,
        )

        with transaction.atomic():
            if payload.text is not None:
                question.text = payload.text
            if payload.category is not None:
                question.category = payload.category
            if payload.update_context:
                question.explanation = payload.context
            if payload.update_answers:
                question.answers.all().delete()
                answers = [
                    Answer(question=question, text=answer_text, is_correct=True)
                    for answer_text in payload.positive_answers
                ] + [
                    Answer(question=question, text=answer_text, is_correct=False)
                    for answer_text in payload.negative_answers
                ]
                Answer.objects.bulk_create(answers)

            question.needs_rework = False
            question.save()
            return question

    def _build_payload(
        self,
        *,
        text: str | None,
        category_id: int | None,
        category_name: str | None,
        context: str | None,
        positive_answers: Iterable[str] | None,
        negative_answers: Iterable[str] | None,
        update_context: bool,
        update_answers: bool,
    ) -> QuestionUpdatePayload:
        cleaned_text = None
        if text is not None:
            cleaned_text = (text or "").strip()
            if not cleaned_text:
                raise QuestionUpdateError("Le champ 'question' est requis.")

        category = None
        if category_id or category_name:
            category = self._resolve_category(
                category_id=category_id, category_name=category_name
            )

        cleaned_context = None
        if update_context:
            cleaned_context = (context or "").strip() or None

        cleaned_positive: Sequence[str] = []
        cleaned_negative: Sequence[str] = []
        if update_answers:
            if positive_answers is None or negative_answers is None:
                raise QuestionUpdateError(
                    "Fournissez 'positive_answers' et 'negative_answers'."
                )
            cleaned_positive = self._clean_answers(positive_answers)
            cleaned_negative = self._clean_answers(negative_answers)
            if not cleaned_positive:
                raise QuestionUpdateError("Fournissez au moins une réponse positive.")
            if not cleaned_negative:
                raise QuestionUpdateError("Fournissez au moins une réponse négative.")

        return QuestionUpdatePayload(
            text=cleaned_text,
            category=category,
            context=cleaned_context,
            update_context=update_context,
            positive_answers=cleaned_positive,
            negative_answers=cleaned_negative,
            update_answers=update_answers,
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
            raise QuestionUpdateError(
                "Spécifiez 'category_id' ou 'category_name'."
            )
        category, _ = Category.objects.get_or_create(name=cleaned_name)
        return category

    @staticmethod
    def _clean_answers(answers: Iterable[str]) -> list[str]:
        return [answer.strip() for answer in answers if answer and answer.strip()]
