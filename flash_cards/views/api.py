from __future__ import annotations

import hmac
import json
from functools import wraps

from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from flash_cards.models import Category, Question
from flash_cards.services import (
    QuestionCreationError,
    QuestionCreationService,
    QuestionUpdateError,
    QuestionUpdateService,
)


class BatchCreationError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def _is_token_valid(request: HttpRequest) -> bool:
    configured_token = getattr(settings, "FLASH_CARDS_MCP_TOKEN", "")
    header_token = request.headers.get("X-MCP-TOKEN", "")
    if not configured_token or not header_token:
        return False
    return hmac.compare_digest(configured_token, header_token)


def _is_authorized(request: HttpRequest) -> bool:
    if request.user.is_authenticated and request.user.is_staff:
        return True
    return _is_token_valid(request)


def require_api_access(view_func):
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if not _is_authorized(request):
            return _json_error("Authentification requise.", status=403)
        return view_func(request, *args, **kwargs)

    return wrapper


@csrf_exempt
@require_POST
@require_api_access
def create_question(request: HttpRequest) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return _json_error("JSON invalide.")

    if isinstance(payload, dict):
        payloads = [payload]
        expect_single = True
    elif isinstance(payload, list):
        if not payload:
            return _json_error("Fournissez au moins un objet JSON.")
        for idx, item in enumerate(payload, start=1):
            if not isinstance(item, dict):
                return _json_error(
                    f"Entrée #{idx} : chaque élément doit être un objet JSON."
                )
        payloads = payload
        expect_single = False
    else:
        return _json_error("Le JSON doit représenter un objet ou un tableau d'objets.")

    normalized_payloads: list[tuple[dict, list, list]] = []
    for idx, entry in enumerate(payloads, start=1):
        positive = entry.get("positive_answers") or []
        negative = entry.get("negative_answers") or []
        if not isinstance(positive, list):
            return _json_error(f"Entrée #{idx} : 'positive_answers' doit être un tableau.")
        if not isinstance(negative, list):
            return _json_error(f"Entrée #{idx} : 'negative_answers' doit être un tableau.")
        normalized_payloads.append((entry, positive, negative))

    service = QuestionCreationService()
    try:
        with transaction.atomic():
            created_questions = []
            for idx, (entry, positive, negative) in enumerate(
                normalized_payloads, start=1
            ):
                try:
                    question = service.create_question(
                        text=entry.get("question", ""),
                        category_id=entry.get("category_id"),
                        category_name=entry.get("category"),
                        context=entry.get("context"),
                        positive_answers=positive,
                        negative_answers=negative,
                    )
                except Category.DoesNotExist as exc:
                    raise BatchCreationError(
                        f"Entrée #{idx} : Catégorie introuvable.", status=404
                    ) from exc
                except QuestionCreationError as exc:
                    raise BatchCreationError(f"Entrée #{idx} : {exc}") from exc
                created_questions.append(question)
    except BatchCreationError as exc:
        return _json_error(str(exc), status=exc.status)

    serialized = [_serialize_question(question) for question in created_questions]
    if expect_single:
        return JsonResponse(serialized[0], status=201)
    return JsonResponse({"created": serialized, "count": len(serialized)}, status=201)


@require_GET
@require_api_access
def list_categories(request: HttpRequest) -> JsonResponse:
    categories = (
        Category.objects.annotate(question_count=Count("questions"))
        .order_by("name")
        .values("id", "name", "question_count")
    )
    return JsonResponse({"categories": list(categories)})


@require_GET
@require_api_access
def needs_rework_question(request: HttpRequest) -> JsonResponse:
    question = (
        Question.objects.filter(needs_rework=True)
        .select_related("category")
        .prefetch_related("answers")
        .order_by("?")
        .first()
    )
    if not question:
        return _json_error("Aucune question à retravailler.", status=404)
    return JsonResponse(_serialize_question(question))


@csrf_exempt
@require_POST
@require_api_access
def update_question(request: HttpRequest, question_id: int) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return _json_error("JSON invalide.")
    if not isinstance(payload, dict):
        return _json_error("Le JSON doit représenter un objet.")

    question = Question.objects.filter(pk=question_id).first()
    if not question:
        return _json_error("Question introuvable.", status=404)

    update_context = "context" in payload
    update_answers = "positive_answers" in payload or "negative_answers" in payload
    text = payload.get("question") if "question" in payload else None
    context = payload.get("context") if update_context else None
    category_id = payload.get("category_id") if "category_id" in payload else None
    category_name = payload.get("category") if "category" in payload else None
    positive_answers = (
        payload.get("positive_answers") if "positive_answers" in payload else None
    )
    negative_answers = (
        payload.get("negative_answers") if "negative_answers" in payload else None
    )

    if positive_answers is not None and not isinstance(positive_answers, list):
        return _json_error("'positive_answers' doit être un tableau.")
    if negative_answers is not None and not isinstance(negative_answers, list):
        return _json_error("'negative_answers' doit être un tableau.")

    service = QuestionUpdateService()
    try:
        question = service.update_question(
            question=question,
            text=text,
            category_id=category_id,
            category_name=category_name,
            context=context,
            positive_answers=positive_answers,
            negative_answers=negative_answers,
            update_context=update_context,
            update_answers=update_answers,
        )
    except Category.DoesNotExist as exc:
        return _json_error("Catégorie introuvable.", status=404)
    except QuestionUpdateError as exc:
        return _json_error(str(exc))

    question.refresh_from_db()
    question = (
        Question.objects.select_related("category")
        .prefetch_related("answers")
        .get(pk=question.pk)
    )
    return JsonResponse(_serialize_question(question))


def _serialize_question(question):
    positive_created = list(
        question.answers.filter(is_correct=True).values_list("text", flat=True)
    )
    negative_created = list(
        question.answers.filter(is_correct=False).values_list("text", flat=True)
    )
    return {
        "id": question.id,
        "question": question.text,
        "context": question.explanation,
        "category": {
            "id": question.category_id,
            "name": question.category.name,
        },
        "positive_answers": positive_created,
        "negative_answers": negative_created,
    }
