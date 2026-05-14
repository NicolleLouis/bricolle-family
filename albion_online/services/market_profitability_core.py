class AlbionMarketProfitabilityCore:
    def _build_craft_margin_percent(self, craft_margin, craft_cost):
        if craft_margin is None or craft_cost in (None, 0):
            return None
        return (craft_margin / craft_cost) * 100
