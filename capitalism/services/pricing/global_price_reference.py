from typing import Dict

from django.apps import apps

from capitalism.constants.object_type import ObjectType


class GlobalPriceReferenceService:
    """Return canonical reference prices used across the simulation."""

    class PriceNotFound(Exception):
        """Raised when no reference price exists for the requested object."""

    DEFAULT_PRICE_MAP: Dict[str, float] = {
        ObjectType.WHEAT: 1.0,
        ObjectType.WOOD: 2.0,
        ObjectType.BREAD: 7.0,
        ObjectType.FLOUR: 4.0,
        ObjectType.SCYTHE: 100.0,
        ObjectType.AXE: 100.0,
        ObjectType.PICKAXE: 100.0,
        ObjectType.SPATULA: 100.0,
        ObjectType.ORE: 10.0,
    }

    def get_reference_price(self, object_type: str) -> float:
        model = self._model()
        try:
            entry = model.objects.get(object=object_type)
        except model.DoesNotExist:
            return self._default_price(object_type)
        return entry.perceived_price

    def get_default_price(self, object_type: str) -> float:
        return self._default_price(object_type)

    def _default_price(self, object_type: str) -> float:
        try:
            return self.DEFAULT_PRICE_MAP[object_type]
        except KeyError as exc:  # noqa: PERF203 small map
            raise self.PriceNotFound(f"No price reference defined for {object_type}.") from exc

    def _model(self):
        return apps.get_model("capitalism", "MarketPerceivedPrice")
