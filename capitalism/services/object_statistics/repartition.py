from __future__ import annotations

from typing import Dict, List

from django.apps import apps


class HumanObjectRepartitionService:
    """Aggregate object counts per type for a given human."""

    def __init__(self, human_id: int):
        self.human_id = human_id
        self.object_model = apps.get_model("capitalism", "Object")

    def run(self) -> List[Dict[str, object]]:
        labels = dict(self.object_model._meta.get_field("type").choices)  # type: ignore[attr-defined]
        queryset = (
            self.object_model.objects.filter(owner_id=self.human_id)
            .values("type")
            .order_by("type")
        )

        counts: Dict[str, int] = {}
        for row in queryset:
            obj_type = row["type"]
            counts[obj_type] = counts.get(obj_type, 0) + 1

        return [
            {
                "type": obj_type,
                "label": labels.get(obj_type, obj_type),
                "quantity": quantity,
            }
            for obj_type, quantity in counts.items()
        ]
