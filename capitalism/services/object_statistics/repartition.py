from __future__ import annotations

from typing import Dict, List

from django.apps import apps
from django.db import models


class HumanObjectRepartitionService:
    """Aggregate object counts per type for a given human."""

    def __init__(self, human_id: int):
        self.human_id = human_id
        self.object_model = apps.get_model("capitalism", "ObjectStack")

    def run(self) -> List[Dict[str, object]]:
        labels = dict(self.object_model._meta.get_field("type").choices)  # type: ignore[attr-defined]
        queryset = (
            self.object_model.objects.filter(owner_id=self.human_id)
            .values("type")
            .annotate(quantity=models.Sum("quantity"))
            .order_by("type")
        )

        return [
            {
                "type": object_type,
                "label": labels.get(object_type, object_type),
                "quantity": quantity,
            }
            for object_type, quantity in (
                (row["type"], int(row["quantity"] or 0)) for row in queryset
            )
        ]
