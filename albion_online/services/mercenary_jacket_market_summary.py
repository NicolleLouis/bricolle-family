from collections import defaultdict
from dataclasses import dataclass
from statistics import mean

from albion_online.constants.city import City
from albion_online.constants.object_type import ObjectType
from albion_online.models import Price


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
    sell_price: int | None
    sell_price_freshness: dict[str, str] | None
    buy_price_freshness: dict[str, str] | None
    total_cost: int | None
    is_hidden: bool


@dataclass(frozen=True)
class CityPriceDetail:
    city: str
    label: str
    craft_cost: int | None
    craft_margin: int | None
    is_hidden: bool
    input_details: list[InputPriceDetail]
    quality_details: list[QualityPriceDetail]


class MercenaryJacketMarketSummaryService:
    QUALITIES_TO_AVERAGE = (0, 1, 2)
    TRADE_FEE_RATE = 0.02
    DEFAULT_RESOURCE_RETURN_RATE = 0.153
    SPECIALIZED_RESOURCE_RETURN_RATE = 0.367
    RESOURCE_INPUT_TYPES = {
        ObjectType.CLOTH,
        ObjectType.LEATHER,
        ObjectType.METALBAR,
        ObjectType.PLANKS,
        ObjectType.STONEBLOCK,
    }
    QUALITY_LABELS = {
        0: "Normal",
        1: "Good",
        2: "Outstanding",
        3: "Excellent",
        4: "Masterpiece",
    }

    def build_rows(self, objects) -> list[dict]:
        rows = []
        for albion_object in objects:
            prices = list(albion_object.prices.all())
            recipe = albion_object.output_recipes.first()
            rows.append(
                {
                    "object": albion_object,
                    "city_summaries": self._build_city_summaries(prices, recipe),
                    "city_details": self._build_city_details(prices, recipe),
                }
            )
        return rows

    def _build_city_summaries(self, prices, recipe) -> list[CityMarketSummary]:
        prices_by_city_and_quality = self._build_latest_price_index(prices)
        city_summaries = []
        for city, label in City.choices:
            city_summaries.append(
                self._build_city_summary(
                    city=city,
                    label=label,
                    prices_by_quality=prices_by_city_and_quality.get(city, {}),
                    recipe=recipe,
                )
            )
        return city_summaries

    def _build_latest_price_index(self, prices):
        prices_by_city_and_quality = defaultdict(dict)
        for price in prices:
            if price.quality not in self.QUALITIES_TO_AVERAGE:
                continue

            city_prices = prices_by_city_and_quality[price.city]
            if price.quality not in city_prices:
                city_prices[price.quality] = price
        return prices_by_city_and_quality

    def _build_city_summary(self, city, label, prices_by_quality, recipe) -> CityMarketSummary:
        sell_price, sell_price_freshness, buy_price_freshness = self._build_city_price_summary(prices_by_quality)
        input_details = self._build_input_details(recipe, city) if recipe is not None else []
        is_hidden = self._is_stale_freshness(sell_price_freshness) or self._is_stale_freshness(
            buy_price_freshness
        ) or any(input_detail.is_hidden for input_detail in input_details)
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

        craft_cost = self._build_craft_cost_from_input_details(input_details) if input_details else None
        net_sell_price = self._apply_trade_fee_to_sell_price(sell_price)
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

    def _build_average_price(self, prices) -> int | None:
        if not prices:
            return None
        return int(round(mean(prices)))

    def _build_city_details(self, prices, recipe) -> list[CityPriceDetail]:
        prices_by_city_and_quality = self._build_latest_price_index(prices)
        city_details = []
        for city, label in City.choices:
            city_details.append(
                self._build_city_detail(
                    city=city,
                    label=label,
                    prices_by_quality=prices_by_city_and_quality.get(city, {}),
                    recipe=recipe,
                )
            )
        return city_details

    def _build_city_detail(self, city, label, prices_by_quality, recipe) -> CityPriceDetail:
        input_details = self._build_input_details(recipe, city) if recipe is not None else []
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
        craft_cost = self._build_craft_cost_from_input_details(input_details) if input_details else None
        sell_price, _, _ = self._build_city_price_summary(prices_by_quality)
        net_sell_price = self._apply_trade_fee_to_sell_price(sell_price)
        craft_margin = None if net_sell_price is None or craft_cost is None else net_sell_price - craft_cost
        return CityPriceDetail(
            city=city,
            label=label,
            craft_cost=craft_cost,
            craft_margin=craft_margin,
            is_hidden=is_hidden,
            input_details=input_details,
            quality_details=quality_details,
        )

    def _build_input_details(self, recipe, city) -> list[InputPriceDetail]:
        input_details = []
        resource_return_rate = self._build_resource_return_rate(recipe, city)
        for recipe_input in recipe.inputs.all():
            sell_price, sell_price_freshness, buy_price_freshness = self._build_city_price_summary(
                self._build_latest_price_index(recipe_input.object.prices.all()).get(city, {})
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
                    sell_price=sell_price,
                    sell_price_freshness=sell_price_freshness,
                    buy_price_freshness=buy_price_freshness,
                    total_cost=total_cost,
                    is_hidden=is_hidden,
                )
            )
        return input_details

    def _build_craft_cost(self, recipe, city) -> int | None:
        input_details = self._build_input_details(recipe, city)
        return self._build_craft_cost_from_input_details(input_details)

    def _build_resource_return_rate(self, recipe, city) -> float:
        if recipe is None or recipe.output is None:
            return self.DEFAULT_RESOURCE_RETURN_RATE

        if recipe.output.type is not None and recipe.output.type.resource_return_rate_city == city:
            return self.SPECIALIZED_RESOURCE_RETURN_RATE
        return self.DEFAULT_RESOURCE_RETURN_RATE

    def _build_input_total_cost(
        self,
        quantity: int,
        sell_price: int | None,
        object_type: str,
        resource_return_rate: float,
    ) -> int | None:
        if sell_price is None:
            return None

        total_cost = quantity * sell_price
        if object_type in self.RESOURCE_INPUT_TYPES:
            total_cost *= 1 - resource_return_rate
        return int(round(total_cost))

    def _build_city_price_summary(self, prices_by_quality) -> tuple[int | None, dict[str, str] | None, dict[str, str] | None]:
        selected_prices = [
            price
            for quality in self.QUALITIES_TO_AVERAGE
            if (price := prices_by_quality.get(quality)) is not None
        ]
        if not selected_prices:
            return None, None, None
        sell_prices = [price.sell_price_min for price in selected_prices if price.sell_price_min is not None]
        buy_prices = [price.buy_price_max for price in selected_prices if price.buy_price_max is not None]
        sell_dates = [price.sell_price_min_date for price in selected_prices if price.sell_price_min_date is not None]
        buy_dates = [price.buy_price_max_date for price in selected_prices if price.buy_price_max_date is not None]
        return (
            self._build_average_price(sell_prices),
            Price.build_freshness(min(sell_dates)) if sell_dates else None,
            Price.build_freshness(min(buy_dates)) if buy_dates else None,
        )

    def _is_stale_freshness(self, freshness: dict[str, str] | None) -> bool:
        return freshness is not None and freshness.get("class_name") == "bg-danger"

    def _build_craft_cost_from_input_details(self, input_details: list[InputPriceDetail]) -> int | None:
        if not input_details:
            return None
        if any(input_detail.total_cost is None for input_detail in input_details):
            return None
        raw_cost = sum(input_detail.total_cost for input_detail in input_details if input_detail.total_cost is not None)
        return self._apply_trade_fee_to_craft_cost(raw_cost)

    def _build_margin_class_name(self, craft_margin) -> str | None:
        if craft_margin is None:
            return None
        if craft_margin < 0:
            return "bg-danger"
        return "bg-success"

    def _build_craft_margin_percent(self, craft_margin: int | None, craft_cost: int | None) -> float | None:
        if craft_margin is None or craft_cost in (None, 0):
            return None
        return (craft_margin / craft_cost) * 100

    def _apply_trade_fee_to_craft_cost(self, craft_cost: int) -> int:
        return int(round(craft_cost * (1 + self.TRADE_FEE_RATE)))

    def _apply_trade_fee_to_sell_price(self, sell_price: int | None) -> int | None:
        if sell_price is None:
            return None
        return int(round(sell_price * (1 - self.TRADE_FEE_RATE)))
