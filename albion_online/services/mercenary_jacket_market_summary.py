from dataclasses import dataclass

from albion_online.constants.city import City
from albion_online.constants.leather_jacket import LEATHER_JACKET_TYPES
from albion_online.constants.object_type import ObjectType
from albion_online.models import Price
from albion_online.services.market_summary_core import AlbionMarketSummaryCore


@dataclass(frozen=True)
class CityMarketSummary:
    city: str
    label: str
    sell_price: int | None
    craft_cost: int | None
    craft_margin: int | None
    craft_margin_percent: float | None
    craft_margin_class_name: str | None
    sell_price_freshness: dict[str, str] | None
    is_hidden: bool


@dataclass(frozen=True)
class QualityPriceDetail:
    quality: int
    label: str
    sell_price: int | None
    buy_price: int | None
    sell_price_freshness: dict[str, str] | None
    buy_price_freshness: dict[str, str] | None
    is_hidden: bool


@dataclass(frozen=True)
class InputPriceDetail:
    label: str
    quantity: int
    raw_cost: int | None
    resource_return_rate: float | None
    resource_return_amount: int | None
    sell_price: int | None
    sell_price_freshness: dict[str, str] | None
    buy_price_freshness: dict[str, str] | None
    total_cost: int | None
    is_hidden: bool


@dataclass(frozen=True)
class CityPriceDetail:
    city: str
    label: str
    sell_price: int | None
    raw_input_cost: int | None
    input_cost_before_buy_tax: int | None
    resource_return_rate: float | None
    resource_return_amount: int | None
    buy_tax_amount: int | None
    sale_fee_amount: int | None
    net_sell_price: int | None
    craft_cost: int | None
    craft_margin: int | None
    is_hidden: bool
    input_details: list[InputPriceDetail]
    quality_details: list[QualityPriceDetail]


class MercenaryJacketMarketSummaryService(AlbionMarketSummaryCore):
    BUY_TAX_RATE = 0.02
    SALE_TAX_RATE = 0.04
    LISTING_TAX_RATE = 0.025
    SALE_NET_FACTOR = 1 - SALE_TAX_RATE - LISTING_TAX_RATE
    RESOURCE_INPUT_TYPES = {
        ObjectType.CLOTH,
        ObjectType.LEATHER,
        ObjectType.METALBAR,
        ObjectType.PLANKS,
        ObjectType.STONEBLOCK,
    }

    def build_rows(self, objects) -> list[dict]:
        return [self._build_row(albion_object, include_details=False) for albion_object in objects]

    def build_detail_row(self, albion_object) -> dict:
        return self._build_row(albion_object, include_details=True)

    def _build_row(self, albion_object, include_details: bool) -> dict:
        prices = list(albion_object.prices.all())
        recipe = albion_object.output_recipes.first()
        prices_by_city_and_quality = self._build_latest_price_index(prices)
        recipe_input_prices_by_object = self._build_recipe_input_price_indexes(recipe)
        jacket_type = self._find_jacket_type(albion_object.aodp_id)
        row = {
            "object": albion_object,
            "city_summaries": self._build_city_summaries(
                prices_by_city_and_quality,
                recipe,
                recipe_input_prices_by_object,
            ),
            "detail_key": f"{jacket_type['key']}:{albion_object.tier_enchantment_notation}",
        }
        if include_details:
            row["city_details"] = self._build_city_details(
                prices_by_city_and_quality,
                recipe,
                recipe_input_prices_by_object,
            )
        return row

    def _find_jacket_type(self, aodp_id):
        for jacket_type in LEATHER_JACKET_TYPES:
            if jacket_type["aodp_id_fragment"] in aodp_id:
                return jacket_type
        return {"key": "unknown", "label": "Unknown", "aodp_id_fragment": ""}

    def _build_recipe_input_price_indexes(self, recipe):
        if recipe is None:
            return {}
        return {
            recipe_input.object_id: self._build_latest_price_index(recipe_input.object.prices.all())
            for recipe_input in recipe.inputs.all()
        }

    def _build_city_summaries(self, prices_by_city_and_quality, recipe, recipe_input_prices_by_object) -> list[CityMarketSummary]:
        city_summaries = []
        for city, label in City.choices:
            city_summaries.append(
                self._build_city_summary(
                    city=city,
                    label=label,
                    prices_by_quality=prices_by_city_and_quality.get(city, {}),
                    recipe=recipe,
                    recipe_input_prices_by_object=recipe_input_prices_by_object,
                )
            )
        return city_summaries

    def _build_city_summary(self, city, label, prices_by_quality, recipe, recipe_input_prices_by_object) -> CityMarketSummary:
        sell_price, sell_price_freshness, buy_price_freshness = self._build_city_price_summary(prices_by_quality)
        craft_cost, has_stale_inputs, _, _ = self._build_craft_cost_breakdown(
            recipe,
            city,
            recipe_input_prices_by_object,
        )
        is_hidden = (
            self._is_stale_freshness(sell_price_freshness)
            or self._is_stale_freshness(buy_price_freshness)
            or has_stale_inputs
        )
        if sell_price is None:
            return CityMarketSummary(
                city=city,
                label=label,
                sell_price=None,
                craft_cost=None,
                craft_margin=None,
                craft_margin_percent=None,
                craft_margin_class_name=None,
                sell_price_freshness=None,
                is_hidden=is_hidden,
            )

        net_sell_price = self._apply_sale_fees_to_sell_price(sell_price)
        craft_margin = None if craft_cost is None or net_sell_price is None else net_sell_price - craft_cost
        craft_margin_percent = self._build_craft_margin_percent(craft_margin, craft_cost)
        return CityMarketSummary(
            city=city,
            label=label,
            sell_price=sell_price,
            craft_cost=None if is_hidden else craft_cost,
            craft_margin=None if is_hidden else craft_margin,
            craft_margin_percent=None if is_hidden else craft_margin_percent,
            craft_margin_class_name=self._build_margin_class_name(craft_margin) if not is_hidden else None,
            sell_price_freshness=sell_price_freshness,
            is_hidden=is_hidden,
        )

    def _build_city_details(self, prices_by_city_and_quality, recipe, recipe_input_prices_by_object) -> list[CityPriceDetail]:
        city_details = []
        for city, label in City.choices:
            city_details.append(
                self._build_city_detail(
                    city=city,
                    label=label,
                    prices_by_quality=prices_by_city_and_quality.get(city, {}),
                    recipe=recipe,
                    recipe_input_prices_by_object=recipe_input_prices_by_object,
                )
            )
        return city_details

    def _build_city_detail(self, city, label, prices_by_quality, recipe, recipe_input_prices_by_object) -> CityPriceDetail:
        input_details = self._build_input_details(recipe, city, recipe_input_prices_by_object) if recipe is not None else []
        quality_details = []
        for quality in range(5):
            price = prices_by_quality.get(quality)
            sell_price_freshness = (
                Price.build_freshness(price.sell_price_min_date) if price is not None else None
            )
            buy_price_freshness = (
                Price.build_freshness(price.buy_price_max_date) if price is not None else None
            )
            quality_details.append(
                QualityPriceDetail(
                    quality=quality,
                    label=self.QUALITY_LABELS[quality],
                    sell_price=price.sell_price_min if price is not None else None,
                    buy_price=price.buy_price_max if price is not None else None,
                    sell_price_freshness=sell_price_freshness,
                    buy_price_freshness=buy_price_freshness,
                    is_hidden=self._is_stale_freshness(sell_price_freshness)
                    or self._is_stale_freshness(buy_price_freshness),
                )
            )
        is_hidden = any(quality_detail.is_hidden for quality_detail in quality_details) or any(
            input_detail.is_hidden for input_detail in input_details
        )
        craft_cost, _, raw_input_cost, input_cost_before_buy_tax = self._build_craft_cost_breakdown(
            recipe,
            city,
            recipe_input_prices_by_object,
        )
        sell_price, _, _ = self._build_city_price_summary(prices_by_quality)
        net_sell_price = self._apply_sale_fees_to_sell_price(sell_price)
        craft_margin = None if net_sell_price is None or craft_cost is None else net_sell_price - craft_cost
        has_resource_inputs = any(
            input_detail.resource_return_rate is not None for input_detail in input_details
        )
        resource_return_rate = self._build_resource_return_rate(recipe, city) if has_resource_inputs else None
        resource_return_amount = (
            None
            if not has_resource_inputs or raw_input_cost is None or input_cost_before_buy_tax is None
            else raw_input_cost - input_cost_before_buy_tax
        )
        buy_tax_amount = (
            None
            if craft_cost is None or input_cost_before_buy_tax is None
            else craft_cost - input_cost_before_buy_tax
        )
        sale_fee_amount = None if sell_price is None or net_sell_price is None else sell_price - net_sell_price
        return CityPriceDetail(
            city=city,
            label=label,
            sell_price=sell_price,
            raw_input_cost=raw_input_cost,
            input_cost_before_buy_tax=input_cost_before_buy_tax,
            resource_return_rate=resource_return_rate,
            resource_return_amount=resource_return_amount,
            buy_tax_amount=buy_tax_amount,
            sale_fee_amount=sale_fee_amount,
            net_sell_price=net_sell_price,
            craft_cost=craft_cost,
            craft_margin=craft_margin,
            is_hidden=is_hidden,
            input_details=input_details,
            quality_details=quality_details,
        )

    def _build_input_details(self, recipe, city, recipe_input_prices_by_object) -> list[InputPriceDetail]:
        input_details = []
        resource_return_rate = self._build_resource_return_rate(recipe, city)
        for recipe_input in recipe.inputs.all():
            city_prices_by_quality = recipe_input_prices_by_object.get(recipe_input.object_id, {}).get(city, {})
            sell_price, sell_price_freshness, buy_price_freshness = self._build_city_price_summary(
                city_prices_by_quality
            )
            raw_cost = None if sell_price is None else recipe_input.quantity * sell_price
            resource_return_amount = None
            if raw_cost is not None and recipe_input.object.type_code in self.RESOURCE_INPUT_TYPES:
                resource_return_amount = raw_cost - self._build_input_total_cost(
                    quantity=recipe_input.quantity,
                    sell_price=sell_price,
                    object_type=recipe_input.object.type_code,
                    resource_return_rate=resource_return_rate,
                )
            total_cost = self._build_input_total_cost(
                quantity=recipe_input.quantity,
                sell_price=sell_price,
                object_type=recipe_input.object.type_code,
                resource_return_rate=resource_return_rate,
            )
            is_hidden = self._is_stale_freshness(sell_price_freshness) or self._is_stale_freshness(
                buy_price_freshness
            )
            input_details.append(
                InputPriceDetail(
                    label=recipe_input.object.display_name,
                    quantity=recipe_input.quantity,
                    raw_cost=raw_cost,
            resource_return_rate=resource_return_rate if recipe_input.object.type_code in self.RESOURCE_INPUT_TYPES else None,
                    resource_return_amount=resource_return_amount,
                    sell_price=sell_price,
                    sell_price_freshness=sell_price_freshness,
                    buy_price_freshness=buy_price_freshness,
                    total_cost=total_cost,
                    is_hidden=is_hidden,
                )
            )
        return input_details

    def _build_craft_cost_for_summary(self, recipe, city, recipe_input_prices_by_object) -> tuple[int | None, bool]:
        craft_cost, has_stale_inputs, _, _ = self._build_craft_cost_breakdown(
            recipe,
            city,
            recipe_input_prices_by_object,
        )
        return craft_cost, has_stale_inputs

    def _build_craft_cost_breakdown(
        self,
        recipe,
        city,
        recipe_input_prices_by_object,
    ) -> tuple[int | None, bool, int | None, int | None]:
        if recipe is None:
            return None, False, None, None

        resource_return_rate = self._build_resource_return_rate(recipe, city)
        raw_input_cost = 0
        input_cost_before_buy_tax = 0
        has_stale_inputs = False
        for recipe_input in recipe.inputs.all():
            city_prices_by_quality = recipe_input_prices_by_object.get(recipe_input.object_id, {}).get(city, {})
            sell_price, sell_price_freshness, buy_price_freshness = self._build_city_price_summary(
                city_prices_by_quality
            )
            has_stale_inputs = has_stale_inputs or self._is_stale_freshness(sell_price_freshness) or self._is_stale_freshness(
                buy_price_freshness
            )
            total_cost = self._build_input_total_cost(
                quantity=recipe_input.quantity,
                sell_price=sell_price,
                object_type=recipe_input.object.type_code,
                resource_return_rate=resource_return_rate,
            )
            if total_cost is None or sell_price is None:
                return None, has_stale_inputs, None, None
            raw_input_cost += recipe_input.quantity * sell_price
            input_cost_before_buy_tax += total_cost
        if input_cost_before_buy_tax == 0:
            return None, has_stale_inputs, None, None
        craft_cost = self._apply_buy_tax_to_craft_cost(input_cost_before_buy_tax)
        return craft_cost, has_stale_inputs, raw_input_cost, input_cost_before_buy_tax

    def _apply_buy_tax_to_craft_cost(self, craft_cost: int) -> int:
        return int(round((craft_cost * 102) / 100))

    def _apply_sale_fees_to_sell_price(self, sell_price: int | None) -> int | None:
        if sell_price is None:
            return None
        return int(round((sell_price * 935) / 1000))
