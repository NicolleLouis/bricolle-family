from typing import Dict

from capitalism.constants.object_type import ObjectType


class GlobalPriceReferenceService:
    """Return canonical reference prices used across the simulation."""

    class PriceNotFound(Exception):
        """Raised when no reference price exists for the requested object."""

    _PRICE_MAP: Dict[str, float] = {
        ObjectType.WHEAT: 1.0,
        ObjectType.WOOD: 2.0,
        ObjectType.BREAD: 10.0,
        ObjectType.FLOUR: 4.0,
        ObjectType.SCYTHE: 100.0,
        ObjectType.AXE: 100.0,
        ObjectType.PICKAXE: 100.0,
        ObjectType.SPATULA: 100.0,
        ObjectType.ORE: 25.0,
    }

    def get_reference_price(self, object_type: str) -> float:
        try:
            return self._PRICE_MAP[object_type]
        except KeyError as exc:  # noqa: PERF203 small map
            raise self.PriceNotFound(f"No price reference defined for {object_type}.") from exc
