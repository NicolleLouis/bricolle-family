import random
from typing import List, Optional

from django.shortcuts import render
from django.utils import timezone

from flash_cards.models import Answer, Question
from flash_cards.services import QuestionRetrievalService


def home(request):
    service = QuestionRetrievalService()
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "next":
            context = _prepare_question_context(service)
        else:
            context = _handle_answer_submission(request, service)
    else:
        context = _prepare_question_context(service)
    return render(request, "flash_cards/home.html", context)


def _handle_answer_submission(request, service):
    question_id = request.POST.get("question_id")
    answer_id = request.POST.get("answer_id")
    answers_order = request.POST.get("answers_order", "")

    if not question_id or not answer_id or not answers_order:
        return _prepare_question_context(service)

    question = Question.objects.prefetch_related("answers").filter(pk=question_id).first()
    if not question:
        return _prepare_question_context(service)

    order_ids = [
        value.strip()
        for value in answers_order.split(",")
        if value.strip()
    ]
    answers = _load_answers(question, order_ids)

    if not answers:
        answers = _select_answers(question)
        if not answers:
            return _prepare_question_context(service)
        order_ids = [str(answer.id) for answer in answers]

    answers_by_id = {str(answer.id): answer for answer in answers}
    selected_answer = answers_by_id.get(str(answer_id))
    if not selected_answer:
        return _prepare_question_context(service)

    correct_answer = next((answer for answer in answers if answer.is_correct), None)
    is_correct = bool(correct_answer and selected_answer.id == correct_answer.id)
    _update_question_stats(question, is_correct)

    return {
        **_base_context(),
        "question": question,
        "answers": answers,
        "answers_order": ",".join(order_ids),
        "answered": True,
        "selected_answer_id": str(selected_answer.id),
        "correct_answer_id": str(correct_answer.id) if correct_answer else None,
        "is_correct": is_correct,
        "correct_answer_text": correct_answer.text if correct_answer else None,
    }


def _prepare_question_context(service):
    for _ in range(5):
        question = service.get_question()
        if not question:
            break
        answers = _select_answers(question)
        if answers:
            return {
                **_base_context(),
                "question": question,
                "answers": answers,
                "answers_order": ",".join(str(answer.id) for answer in answers),
            }
    return _base_context(message="Aucune question disponible pour le moment.")


def _select_answers(question: Question) -> List[Answer]:
    positives = list(question.answers.filter(is_correct=True))
    negatives = list(question.answers.filter(is_correct=False))

    if not positives or not negatives:
        return []

    positive = random.choice(positives)
    if len(negatives) <= 2:
        negative_choices = [random.choice(negatives)]
    else:
        negative_choices = random.sample(negatives, 3)

    options = [positive, *negative_choices]
    random.shuffle(options)
    return options


def _load_answers(question: Question, order_ids: List[str]) -> List[Answer]:
    if not order_ids:
        return []
    answers = list(
        Answer.objects.filter(question=question, id__in=order_ids)
    )
    mapped = {str(answer.id): answer for answer in answers}
    return [mapped[id_] for id_ in order_ids if id_ in mapped]


def _update_question_stats(question: Question, is_correct: bool) -> None:
    question.answer_number += 1
    if is_correct:
        question.positive_answer_number += 1
    else:
        question.negative_answer_number += 1
    question.last_answer_result = is_correct
    question.last_answer = timezone.now()
    question.save(
        update_fields=[
            "answer_number",
            "positive_answer_number",
            "negative_answer_number",
            "last_answer_result",
            "last_answer",
        ]
    )


def _base_context(message: Optional[str] = None):
    return {
        "question": None,
        "answers": [],
        "answers_order": "",
        "answered": False,
        "selected_answer_id": None,
        "correct_answer_id": None,
        "is_correct": None,
        "correct_answer_text": None,
        "message": message,
    }
