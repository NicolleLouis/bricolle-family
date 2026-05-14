from collections import defaultdict
from statistics import mean

from albion_online.models import Price


class AlbionMarketSummaryCore:
    QUALITIES_TO_AVERAGE = (0, 1, 2)
    TRADE_FEE_RATE = 0.02
    DEFAULT_RESOURCE_RETURN_RATE = 0.153
    SPECIALIZED_RESOURCE_RETURN_RATE = 0.367
    RESOURCE_INPUT_TYPES = frozenset()
    QUALITY_LABELS = {
        0: "Normal",
        1: "Good",
        2: "Outstanding",
        3: "Excellent",
        4: "Masterpiece",
    }

    def _build_latest_price_index(self, prices):
        prices_by_city_and_quality = defaultdict(dict)
        for price in prices:
            if price.quality not in self.QUALITIES_TO_AVERAGE:
                continue

            city_prices = prices_by_city_and_quality[price.city]
            if price.quality not in city_prices:
                city_prices[price.quality] = price
        return prices_by_city_and_quality

    def _build_average_price(self, prices) -> int | None:
        if not prices:
            return None
        return int(round(mean(prices)))

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

    def _build_resource_return_rate(self, recipe, city) -> float:
        if recipe is None or recipe.output is None:
            return self.DEFAULT_RESOURCE_RETURN_RATE

        if recipe.output.type is not None and recipe.output.type.resource_return_rate_city == city:
            return self.SPECIALIZED_RESOURCE_RETURN_RATE
        return self.DEFAULT_RESOURCE_RETURN_RATE

    def _build_craft_cost_from_input_details(self, input_details: list) -> int | None:
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

    def _is_stale_freshness(self, freshness: dict[str, str] | None) -> bool:
        return freshness is not None and freshness.get("class_name") == "bg-danger"
