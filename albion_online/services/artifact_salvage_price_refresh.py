from django.db.models import Q

from albion_online.constants.artifact_salvage import ARTIFACT_SALVAGE_FAMILIES
from albion_online.models import Object
from albion_online.services.market_price_refresh_core import GroupedPriceRefreshCore
from albion_online.services.market_summary_querysets import build_market_summary_object_queryset
from albion_online.services.price_fetcher import AlbionOnlineDataPriceFetcher


class ArtifactSalvagePriceRefreshService(GroupedPriceRefreshCore):
    def __init__(self, fetcher=None):
        super().__init__(fetcher or AlbionOnlineDataPriceFetcher())

    def refresh_prices(self) -> list:
        object_groups = [self._get_family_objects(family) for family in ARTIFACT_SALVAGE_FAMILIES]
        return self.refresh_prices_from_groups(object_groups)

    def _get_family_objects(self, family):
        query = Q(aodp_id__contains=family["shard_aodp_id_fragment"])
        for artifact in family["artifacts"]:
            query |= Q(aodp_id__contains=artifact["aodp_id_fragment"])

        return build_market_summary_object_queryset(
            Object.objects.filter(query, tier__gte=6).distinct().order_by("aodp_id")
        )
