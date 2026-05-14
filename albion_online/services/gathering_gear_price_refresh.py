from django.db.models import Q

from albion_online.constants.gathering_gear import GATHERING_GEAR_RESOURCE_GROUPS
from albion_online.models import Object, Price
from albion_online.services.market_price_refresh_core import GroupedPriceRefreshCore
from albion_online.services.price_fetcher import AlbionOnlineDataPriceFetcher


class GatheringGearPriceRefreshService(GroupedPriceRefreshCore):
    def __init__(self, fetcher=None):
        super().__init__(fetcher or AlbionOnlineDataPriceFetcher())

    def refresh_prices(self, selected_resource_filter="all") -> list[Price]:
        selected_resource_groups = GATHERING_GEAR_RESOURCE_GROUPS
        output_groups = [
            self._get_output_objects(resource_group["aodp_id_fragment"])
            for resource_group in selected_resource_groups
        ]
        input_objects = list(self._get_recipe_input_objects(selected_resource_groups))
        output_groups.append(input_objects)
        return self.refresh_prices_from_groups(output_groups)

    def _get_output_objects(self, aodp_id_fragment):
        return Object.objects.filter(
            aodp_id__contains=aodp_id_fragment,
            tier__gte=4,
        ).order_by("aodp_id")

    def _get_recipe_input_objects(self, selected_resource_groups):
        return Object.objects.filter(self._build_recipe_input_query(selected_resource_groups)).distinct().order_by("aodp_id")

    def _build_recipe_input_query(self, selected_resource_groups):
        gear_query = Q()
        for resource_group in selected_resource_groups:
            gear_query |= Q(recipe_inputs__recipe__output__aodp_id__contains=resource_group["aodp_id_fragment"])
        return gear_query
