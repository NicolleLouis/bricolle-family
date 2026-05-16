from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from albion_online.constants.artifact_salvage import ARTIFACT_SALVAGE_FAMILIES
from albion_online.models import Object
from albion_online.services.market_summary_core import AlbionMarketSummaryCore
from albion_online.services.market_summary_querysets import build_market_summary_object_queryset


class ArtifactSalvageMarketSummaryService(AlbionMarketSummaryCore):
    COLUMN_TIERS = (7, 8)
    BUY_ORDER_TAX_RATE = 0.025
    TARGET_MARGIN = 0.10
    SALE_NET_FACTOR = 0.935

    def build_sections(self, selected_city: str) -> list[dict]:
        objects_by_fragment_and_tier = self._build_objects_by_fragment_and_tier()
        sections = []

        for family in ARTIFACT_SALVAGE_FAMILIES:
            shard_price_details_by_tier = {
                tier: self._build_object_price_details(
                    objects_by_fragment_and_tier.get((family["shard_aodp_id_fragment"], tier)),
                    selected_city,
                )
                for tier in self.COLUMN_TIERS
            }
            sections.append(
                {
                    "key": family["key"],
                    "label": family["label"],
                    "columns": [self._build_column(tier) for tier in self.COLUMN_TIERS],
                    "base_row": self._build_base_row(family, shard_price_details_by_tier),
                    "buy_order_row": self._build_buy_order_row(shard_price_details_by_tier),
                    "artifact_rows": self._build_artifact_rows(
                        family,
                        selected_city,
                        shard_price_details_by_tier,
                        objects_by_fragment_and_tier,
                    ),
                }
            )

        return sections

    def _build_objects_by_fragment_and_tier(self):
        tracked_fragments = self._build_tracked_fragments()
        if not tracked_fragments:
            return {}

        query = Q()
        for fragment in tracked_fragments:
            query |= Q(aodp_id__contains=fragment)

        objects = build_market_summary_object_queryset(
            Object.objects.filter(query, tier__in=self.COLUMN_TIERS).distinct()
        )
        return {
            (matching_fragment, albion_object.tier): albion_object
            for albion_object in objects
            if (matching_fragment := self._find_matching_fragment(albion_object.aodp_id)) is not None
        }

    def _build_tracked_fragments(self):
        fragments = []
        for family in ARTIFACT_SALVAGE_FAMILIES:
            fragments.append(family["shard_aodp_id_fragment"])
            fragments.extend(artifact["aodp_id_fragment"] for artifact in family["artifacts"])
        return sorted(set(fragments), key=len, reverse=True)

    def _find_matching_fragment(self, aodp_id: str) -> str | None:
        for fragment in self._build_tracked_fragments():
            if fragment in aodp_id:
                return fragment
        return None

    def _build_column(self, tier: int) -> dict:
        return {"tier": tier, "label": f"T{tier}"}

    def _build_base_row(self, family, shard_price_details_by_tier):
        return {
            "label": f"{family['label']} x10",
            "cells": [
                {
                    "tier": tier,
                    "label": f"T{tier}",
                    "object": None,
                    "price_age_label": shard_price_details_by_tier[tier]["price_age_label"],
                    "current_price": (
                        None
                        if shard_price_details_by_tier[tier]["current_price"] is None
                        else shard_price_details_by_tier[tier]["current_price"] * 10
                    ),
                }
                for tier in self.COLUMN_TIERS
            ],
        }

    def _build_buy_order_row(self, shard_price_details_by_tier):
        return {
            "label": "Buy order",
            "cells": [
                {
                    "tier": tier,
                    "label": f"T{tier}",
                    "object": None,
                    "price_age_label": shard_price_details_by_tier[tier]["price_age_label"],
                    "current_price": self._build_buy_order_price(shard_price_details_by_tier[tier]["current_price"]),
                }
                for tier in self.COLUMN_TIERS
            ],
        }

    def _build_artifact_rows(self, family, selected_city, shard_price_details_by_tier, objects_by_fragment_and_tier):
        rows = []
        for artifact in family["artifacts"]:
            rows.append(
                {
                    "label": artifact["label"],
                    "cells": [
                        self._build_artifact_cell(
                            objects_by_fragment_and_tier.get((artifact["aodp_id_fragment"], tier)),
                            selected_city,
                            shard_price_details_by_tier[tier],
                        )
                        for tier in self.COLUMN_TIERS
                    ],
                }
            )
        return rows

    def _build_artifact_cell(self, albion_object, selected_city, shard_price_details):
        object_price_details = self._build_object_price_details(albion_object, selected_city)
        current_price = object_price_details["current_price"]
        buy_order_price = self._build_buy_order_price(shard_price_details["current_price"])
        return {
            "tier": object_price_details.get("tier"),
            "label": object_price_details.get("label"),
            "object": albion_object,
            "current_price": current_price,
            "price_age_label": object_price_details["price_age_label"],
            "price_state": self._build_price_state(current_price, buy_order_price),
        }

    def _build_object_price_details(self, albion_object, selected_city):
        if albion_object is None:
            return {"tier": None, "label": None, "current_price": None, "price_age_label": None}

        prices_by_city_and_quality = self._build_latest_price_index(albion_object.prices.all())
        city_prices_by_quality = prices_by_city_and_quality.get(selected_city, {})
        sell_price, _, _ = self._build_city_price_summary(city_prices_by_quality)
        return {
            "tier": albion_object.tier,
            "label": f"T{albion_object.tier}" if albion_object.tier is not None else None,
            "current_price": sell_price,
            "price_age_label": self._build_price_age_label(self._build_latest_price_timestamp(city_prices_by_quality)),
        }

    def _build_latest_price_timestamp(self, prices_by_quality):
        selected_prices = [
            price
            for quality in self.QUALITIES_TO_AVERAGE
            if (price := prices_by_quality.get(quality)) is not None
        ]
        if not selected_prices:
            return None

        sell_dates = [price.sell_price_min_date for price in selected_prices if price.sell_price_min_date is not None]
        if not sell_dates:
            return None
        return min(sell_dates)

    def _build_price_age_label(self, timestamp):
        if timestamp is None:
            return None

        age = timezone.now() - timestamp
        rounded_hours = int((age + timedelta(minutes=30)) / timedelta(hours=1))
        hour_label = "heure" if rounded_hours == 1 else "heures"
        return f"Dernier prix: il y a {rounded_hours} {hour_label}"

    def _build_buy_order_price(self, shard_price):
        if shard_price is None:
            return None

        raw_price = (10 * shard_price * self.SALE_NET_FACTOR) / ((1 + self.BUY_ORDER_TAX_RATE) * (1 + self.TARGET_MARGIN))
        return int(round(raw_price))

    def _build_price_state(self, current_price, buy_order_price):
        if current_price is None or buy_order_price is None:
            return None

        if current_price < buy_order_price:
            return "green_strong"
        if current_price * 100 < buy_order_price * 120:
            return "green_pale"
        return "red"
