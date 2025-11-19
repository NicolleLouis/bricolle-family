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

from flash_cards.models import Category
from flash_cards.services import QuestionCreationError, QuestionCreationService


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
