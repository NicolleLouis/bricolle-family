from __future__ import annotations

import hmac
import json
from functools import wraps

from django.conf import settings
from django.db.models import Count
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from flash_cards.models import Category
from flash_cards.services import QuestionCreationError, QuestionCreationService


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

    positive = payload.get("positive_answers") or []
    negative = payload.get("negative_answers") or []
    if not isinstance(positive, list):
        return _json_error("'positive_answers' doit être un tableau.")
    if not isinstance(negative, list):
        return _json_error("'negative_answers' doit être un tableau.")

    service = QuestionCreationService()
    try:
        question = service.create_question(
            text=payload.get("question", ""),
            category_id=payload.get("category_id"),
            category_name=payload.get("category"),
            context=payload.get("context"),
            positive_answers=positive,
            negative_answers=negative,
        )
    except Category.DoesNotExist:
        return _json_error("Catégorie introuvable.", status=404)
    except QuestionCreationError as exc:
        return _json_error(str(exc))

    positive_created = list(
        question.answers.filter(is_correct=True).values_list("text", flat=True)
    )
    negative_created = list(
        question.answers.filter(is_correct=False).values_list("text", flat=True)
    )

    return JsonResponse(
        {
            "id": question.id,
            "question": question.text,
            "context": question.explanation,
            "category": {
                "id": question.category_id,
                "name": question.category.name,
            },
            "positive_answers": positive_created,
            "negative_answers": negative_created,
        },
        status=201,
    )


@require_GET
@require_api_access
def list_categories(request: HttpRequest) -> JsonResponse:
    categories = (
        Category.objects.annotate(question_count=Count("questions"))
        .order_by("name")
        .values("id", "name", "question_count")
    )
    return JsonResponse({"categories": list(categories)})
