from albion_online.constants.object_type import ObjectType
from albion_online.constants.leather_jacket import LEATHER_JACKET_TYPES
from albion_online.models import Object, Price
from albion_online.services.price_fetcher import AlbionOnlineDataPriceFetcher


class LeatherJacketPriceRefreshService:
    def __init__(self, fetcher=None):
        self._fetcher = fetcher or AlbionOnlineDataPriceFetcher()

    def refresh_prices(self) -> list[Price]:
        leather_objects = list(self._get_leather_objects())
        created_prices = []
        for jacket_type in LEATHER_JACKET_TYPES:
            jacket_objects = list(self._get_jacket_objects(jacket_type["aodp_id_fragment"]))
            if jacket_objects:
                created_prices.extend(self._fetcher.fetch_current_prices(jacket_objects))
        if leather_objects:
            created_prices.extend(self._fetcher.fetch_current_prices(leather_objects))
        return created_prices

    def _get_jacket_objects(self, aodp_id_fragment):
        return Object.objects.filter(
            aodp_id__contains=aodp_id_fragment,
            tier__gte=4,
        ).order_by("aodp_id")

    def _get_leather_objects(self):
        return Object.objects.filter(
            type=ObjectType.LEATHER,
            tier__gte=4,
        ).order_by("aodp_id")


MercenaryJacketPriceRefreshService = LeatherJacketPriceRefreshService
