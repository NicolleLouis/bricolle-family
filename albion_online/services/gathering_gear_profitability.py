from albion_online.services.market_profitability_core import AlbionMarketProfitabilityCore


class GatheringGearProfitabilityService(AlbionMarketProfitabilityCore):
    def build_rows(
        self,
        gear_rows,
        selected_city_filter,
        selected_gear_type_filter,
        minimum_percentage,
        minimum_flat,
        sort_by,
        recently_done_keys=None,
    ) -> list[dict]:
        recently_done_keys = recently_done_keys or set()
        rows = []
        for gear_row in gear_rows:
            if not self._matches_gear_type_filter(gear_row, selected_gear_type_filter):
                continue

            for city_summary in self._iter_city_rows(gear_row):
                if not self._matches_city_filter(city_summary, selected_city_filter):
                    continue
                if self._is_recently_done(gear_row, city_summary, recently_done_keys):
                    continue
                if not self._is_profitable(city_summary, minimum_percentage, minimum_flat):
                    continue
                rows.append(self._build_row(gear_row, city_summary))

        rows.sort(key=self._build_sort_key(sort_by))
        return rows

    def _matches_gear_type_filter(self, gear_row, selected_gear_type_filter) -> bool:
        if selected_gear_type_filter == "all":
            return True
        return gear_row["gathering_gear_type_key"] == selected_gear_type_filter

    def _iter_city_rows(self, gear_row):
        return gear_row.get("city_summaries") or gear_row.get("city_details") or []

    def _matches_city_filter(self, city_detail, selected_city_filter) -> bool:
        if selected_city_filter == "all":
            return True
        return city_detail.city == selected_city_filter

    def _is_recently_done(self, gear_row, city_detail, recently_done_keys) -> bool:
        object_identity = getattr(gear_row["object"], "id", None)
        if object_identity is None:
            object_identity = getattr(gear_row["object"], "pk", None)
        return (city_detail.city, object_identity) in recently_done_keys

    def _is_profitable(self, city_detail, minimum_percentage, minimum_flat) -> bool:
        craft_margin_percent = self._build_craft_margin_percent(city_detail.craft_margin, city_detail.craft_cost)
        if city_detail.is_hidden:
            return False
        if city_detail.craft_margin is None or craft_margin_percent is None:
            return False
        if city_detail.craft_margin <= 0:
            return False
        if craft_margin_percent < minimum_percentage:
            return False
        if minimum_flat is not None and city_detail.craft_margin < minimum_flat:
            return False
        return True

    def _build_row(self, gear_row, city_detail) -> dict:
        object_name = gear_row["object"].display_name
        notation = gear_row["object"].tier_enchantment_notation
        if notation:
            object_name = object_name.removesuffix(f" {notation}")

        return {
            "gear_row": gear_row,
            "detail_key": gear_row.get(
                "detail_key",
                f"{gear_row['gathering_gear_type_key']}:{notation or 'unknown'}",
            ),
            "object_title": gear_row["object"].display_name,
            "object": gear_row["object"],
            "object_name": object_name,
            "tier_enchantment_notation": notation,
            "city": city_detail.city,
            "city_label": city_detail.label,
            "gathering_gear_type_key": gear_row["gathering_gear_type_key"],
            "gathering_gear_type_label": gear_row["gathering_gear_type_label"],
            "craft_margin": city_detail.craft_margin,
            "craft_margin_percent": self._build_craft_margin_percent(city_detail.craft_margin, city_detail.craft_cost),
            "craft_cost": city_detail.craft_cost,
        }

    def _build_sort_key(self, sort_by):
        if sort_by == "flat":
            return lambda row: (
                -row["craft_margin"],
                -row["craft_margin_percent"],
                row["city_label"],
                row["object_name"],
                row["tier_enchantment_notation"] or "",
            )
        return lambda row: (
            -row["craft_margin_percent"],
            -row["craft_margin"],
            row["city_label"],
            row["object_name"],
            row["tier_enchantment_notation"] or "",
        )
