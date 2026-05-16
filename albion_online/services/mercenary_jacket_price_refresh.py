from django.db.models import Q

from albion_online.constants.leather_jacket import LEATHER_JACKET_TYPES
from albion_online.models import Object, Price
from albion_online.services.market_price_refresh_core import GroupedPriceRefreshCore
from albion_online.services.price_fetcher import AlbionOnlineDataPriceFetcher


class LeatherJacketPriceRefreshService(GroupedPriceRefreshCore):
    request_log_source = "leather_jacket"

    def __init__(self, fetcher=None):
        super().__init__(fetcher or AlbionOnlineDataPriceFetcher())

    def refresh_prices(self) -> list[Price]:
        input_objects = list(self._get_recipe_input_objects())
        price_groups = [self._get_jacket_objects(jacket_type["aodp_id_fragment"]) for jacket_type in LEATHER_JACKET_TYPES]
        price_groups.append(input_objects)
        return self.refresh_prices_from_groups(price_groups)

    def _get_jacket_objects(self, aodp_id_fragment):
        return Object.objects.filter(
            aodp_id__contains=aodp_id_fragment,
            tier__gte=4,
        ).order_by("aodp_id")

    def _get_recipe_input_objects(self):
        return Object.objects.filter(self._build_jacket_input_query()).distinct().order_by("aodp_id")

    def _build_jacket_input_query(self):
        jacket_query = Q()
        for jacket_type in LEATHER_JACKET_TYPES:
            jacket_query |= Q(recipe_inputs__recipe__output__aodp_id__contains=jacket_type["aodp_id_fragment"])
        return jacket_query


MercenaryJacketPriceRefreshService = LeatherJacketPriceRefreshService
