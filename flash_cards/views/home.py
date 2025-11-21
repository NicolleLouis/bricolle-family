import random
from typing import List, Optional

from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from flash_cards.models import Answer, Question, ThemePreset, QuestionResult
from flash_cards.services import QuestionRetrievalService, ThemePresetQuestionFilterService


def home(request):
    if not request.user.is_authenticated:
        return render(
            request,
            "flash_cards/login_required.html",
            {"login_url": reverse("login")},
        )

    presets = ThemePreset.objects.prefetch_related("categories").order_by("name")
    preset = _get_selected_preset(request, presets)
    base_queryset = Question.objects.all()
    if preset:
        base_queryset = ThemePresetQuestionFilterService(
            preset=preset, queryset=base_queryset
        ).filter_questions()
    service = QuestionRetrievalService(queryset=base_queryset, user=request.user)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "next":
            context = _prepare_question_context(service, presets, preset)
        else:
            context = _handle_answer_submission(request, service, presets, preset)
    else:
        context = _prepare_question_context(service, presets, preset)
    return render(request, "flash_cards/home.html", context)


def _get_selected_preset(request, presets):
    preset_id = request.POST.get("preset_id") or request.GET.get("preset")
    if not preset_id:
        return None
    try:
        preset_id_int = int(preset_id)
    except (TypeError, ValueError):
        return None
    return next((p for p in presets if p.id == preset_id_int), None)


def _handle_answer_submission(request, service, presets, preset):
    question_id = request.POST.get("question_id")
    answer_id = request.POST.get("answer_id")
    answers_order = request.POST.get("answers_order", "")

    if not question_id or not answer_id or not answers_order:
        return _prepare_question_context(service, presets, preset)

    question = Question.objects.prefetch_related("answers").filter(pk=question_id).first()
    if not question:
        return _prepare_question_context(service, presets, preset)

    order_ids = [
        value.strip()
        for value in answers_order.split(",")
        if value.strip()
    ]
    answers = _load_answers(question, order_ids)

    if not answers:
        answers = _select_answers(question)
        if not answers:
            return _prepare_question_context(service, presets, preset)
        order_ids = [str(answer.id) for answer in answers]

    answers_by_id = {str(answer.id): answer for answer in answers}
    selected_answer = answers_by_id.get(str(answer_id))
    if not selected_answer:
        return _prepare_question_context(service, presets, preset)

    correct_answer = next((answer for answer in answers if answer.is_correct), None)
    is_correct = bool(correct_answer and selected_answer.id == correct_answer.id)
    _update_question_stats(question, is_correct)
    _update_user_result(request.user, question, is_correct)

    return {
        **_base_context(presets, preset),
        "question": question,
        "answers": answers,
        "answers_order": ",".join(order_ids),
        "answered": True,
        "selected_answer_id": str(selected_answer.id),
        "correct_answer_id": str(correct_answer.id) if correct_answer else None,
        "is_correct": is_correct,
        "correct_answer_text": correct_answer.text if correct_answer else None,
    }


def _prepare_question_context(service, presets, preset):
    for _ in range(5):
        question = service.get_question()
        if not question:
            break
        answers = _select_answers(question)
        if answers:
            return {
                **_base_context(presets, preset),
                "question": question,
                "answers": answers,
                "answers_order": ",".join(str(answer.id) for answer in answers),
            }
    return _base_context(
        presets, preset, message="Aucune question disponible pour le moment."
    )


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


def _update_user_result(user, question: Question, is_correct: bool) -> None:
    result, _ = QuestionResult.objects.get_or_create(
        user=user,
        question=question,
        defaults={
            "last_answer": timezone.now(),
            "answer_number": 0,
            "positive_answer_number": 0,
            "negative_answer_number": 0,
            "last_answer_result": is_correct,
        },
    )
    result.answer_number += 1
    if is_correct:
        result.positive_answer_number += 1
    else:
        result.negative_answer_number += 1
    result.last_answer_result = is_correct
    result.last_answer = timezone.now()
    result.save(
        update_fields=[
            "answer_number",
            "positive_answer_number",
            "negative_answer_number",
            "last_answer_result",
            "last_answer",
        ]
    )


def _base_context(presets, preset: Optional[ThemePreset], message: Optional[str] = None):
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
        "presets": presets,
        "selected_preset": preset,
        "selected_preset_id": preset.id if preset else "",
    }
