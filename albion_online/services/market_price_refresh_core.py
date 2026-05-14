class GroupedPriceRefreshCore:
    def __init__(self, fetcher):
        self._fetcher = fetcher

    def refresh_prices_from_groups(self, object_groups) -> list:
        created_prices = []
        for objects in object_groups:
            objects = list(objects)
            if not objects:
                continue
            created_prices.extend(self._fetcher.fetch_current_prices(objects))
        return created_prices
