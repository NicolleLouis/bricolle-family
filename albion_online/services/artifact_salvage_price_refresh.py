from django.db.models import Q

from albion_online.constants.artifact_salvage import ARTIFACT_SALVAGE_FAMILIES
from albion_online.models import Object
from albion_online.services.market_price_refresh_core import GroupedPriceRefreshCore
from albion_online.services.market_summary_querysets import build_market_summary_object_queryset
from albion_online.services.price_fetcher import AlbionOnlineDataPriceFetcher


class ArtifactSalvagePriceRefreshService(GroupedPriceRefreshCore):
    request_log_source = "artifact_salvage"

    def __init__(self, fetcher=None):
        super().__init__(fetcher or AlbionOnlineDataPriceFetcher())

    def refresh_prices(self) -> list:
        return self.refresh_prices_from_groups(
            [self._get_family_objects(family) for family in ARTIFACT_SALVAGE_FAMILIES]
        )

    def describe_refresh_targets(self) -> dict:
        family_descriptions = []
        for family in ARTIFACT_SALVAGE_FAMILIES:
            family_objects = list(self._get_family_objects(family))
            family_descriptions.append(
                {
                    "key": family["key"],
                    "label": family["label"],
                    "shard_aodp_id_fragment": family["shard_aodp_id_fragment"],
                    "item_ids": [albion_object.aodp_id for albion_object in family_objects],
                    "count": len(family_objects),
                }
            )

        all_objects = [albion_object for family in family_descriptions for albion_object in family["item_ids"]]
        return {
            "batch_count": sum(1 for family in family_descriptions if family["count"]),
            "count": len(all_objects),
            "item_ids": all_objects,
            "families": family_descriptions,
        }

    def _get_all_objects(self):
        query = Q()
        for family in ARTIFACT_SALVAGE_FAMILIES:
            query |= self._build_family_query(family)
        return build_market_summary_object_queryset(
            Object.objects.filter(query, tier__gte=6).distinct().order_by("aodp_id")
        )

    def _get_family_objects(self, family):
        return build_market_summary_object_queryset(
            Object.objects.filter(self._build_family_query(family), tier__gte=6).distinct().order_by("aodp_id")
        )

    def _build_family_query(self, family):
        query = Q(aodp_id__contains=family["shard_aodp_id_fragment"])
        for artifact in family["artifacts"]:
            query |= Q(aodp_id__contains=artifact["aodp_id_fragment"])
        return query
