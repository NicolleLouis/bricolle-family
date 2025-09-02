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
        sell_cost = total_interest

        diagnostic_fee = SellConstants.DIAGNOSTIC
        sell_cost += diagnostic_fee

        if simulation.use_real_estate_firm:
            agency_fee = float(simulation.house_cost) * SellConstants.AGENCY_FEE
            sell_cost += agency_fee
        self.sell_cost = sell_cost

        month = self.month + 1
        if simulation.duration_before_usable is not None:
            month -= simulation.duration_before_usable
            if month < 0:
                month = 0

        if simulation.comparative_rent is not None:
            rent_equivalent = month * simulation.comparative_rent
            self.net_sell_cost = float(rent_equivalent) - sell_cost
