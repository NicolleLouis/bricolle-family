from dataclasses import dataclass

from finance_simulator.constants.sell import SellConstants


@dataclass
class AmortizationMonth:
    month: int
    interests: float
    capital_paid: float
    capital_remaining: float
    sell_cost: float | None = None
    net_sell_cost: float | None = None

    def compute_sell_cost(self, simulation, total_interest):
        diagnostic_fee = SellConstants.DIAGNOSTIC
        agency_fee = float(simulation.house_cost) * SellConstants.AGENCY_FEE
        sell_cost = diagnostic_fee + agency_fee + total_interest
        self.sell_cost = sell_cost

        if simulation.comparative_rent is not None:
            rent_equivalent = (self.month + 1) * simulation.comparative_rent
            self.net_sell_cost = float(rent_equivalent) - sell_cost
