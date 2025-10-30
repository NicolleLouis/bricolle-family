from __future__ import annotations

from typing import Any, Dict

from django.apps import apps
from django.db.models import QuerySet

from capitalism.constants.object_type import ObjectType


class TransactionListingService:
    """Retrieve transactions with optional filtering by object type."""

    def __init__(self, *, object_type: str | None = None):
        self._selected_object_type = self._normalize_object_type(object_type)
        self._transaction_model = apps.get_model("capitalism", "Transaction")

    def run(self) -> Dict[str, Any]:
        transactions = self._filtered_transactions()
        return {
            "transactions": transactions,
            "object_types": ObjectType.choices,
            "selected_object_type": self._selected_object_type,
        }

    def _normalize_object_type(self, object_type: str | None) -> str | None:
        if not object_type:
            return None
        if object_type in ObjectType.values:
            return object_type
        return None

    def _filtered_transactions(self) -> QuerySet:
        queryset = self._transaction_model.objects.order_by("-id")
        if self._selected_object_type:
            queryset = queryset.filter(object_type=self._selected_object_type)
        return queryset
