from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, Price
from albion_online.services.price_fetcher import AlbionOnlineDataPriceFetcher


class MercenaryJacketPriceRefreshService:
    MERCENARY_JACKET_ID_FRAGMENT = "ARMOR_LEATHER_SET1"

    def __init__(self, fetcher=None):
        self._fetcher = fetcher or AlbionOnlineDataPriceFetcher()

    def refresh_prices(self) -> list[Price]:
        mercenary_jackets = list(self._get_mercenary_jackets())
        if not mercenary_jackets:
            return []
        leather_objects = list(self._get_leather_objects())
        created_prices = []
        created_prices.extend(self._fetcher.fetch_current_prices(mercenary_jackets))
        if leather_objects:
            created_prices.extend(self._fetcher.fetch_current_prices(leather_objects))
        return created_prices

    def _get_mercenary_jackets(self):
        return Object.objects.filter(
            aodp_id__contains=self.MERCENARY_JACKET_ID_FRAGMENT,
        ).order_by("aodp_id")

    def _get_leather_objects(self):
        return Object.objects.filter(
            type=ObjectType.LEATHER,
            tier__gte=4,
        ).order_by("aodp_id")
