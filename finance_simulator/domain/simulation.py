from dataclasses import dataclass


@dataclass
class Simulation:
    house_cost: int
    initial_contribution: int
    duration: int
    annual_rate: float
    comparative_rent: float | None = None
    duration_before_usable: int | None = None
    use_real_estate_firm: bool = True
    sell_price_change: float | None = None

    @property
    def capital(self):
        return self.house_cost - self.initial_contribution

    @property
    def monthly_interest_rate(self):
        return 0.01 * float(self.annual_rate) / 12

    @property
    def duration_in_month(self):
        return self.duration * 12

    @property
    def sell_price(self):
        return (100 + self.sell_price_change) * self.house_cost
