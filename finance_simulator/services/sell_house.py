from __future__ import annotations

from finance_simulator.constants.sell import SellConstants
from finance_simulator.models import Simulation

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from finance_simulator.domain.amortization_month import AmortizationMonth



class SellHouseService:
    def __init__(self, simulation: Simulation, amortization_month: AmortizationMonth):
        self.simulation = simulation
        self.amortization_month = amortization_month
        self.month = self.amortization_month.month + 1

    def compute_sell_cost(self):
        sell_cost = 0
        sell_cost += self.diagnostic_cost()
        sell_cost += self.real_estate_firm_cost()
        sell_cost += self.house_price_evolution()
        sell_cost += self.monthly_expenses()
        return sell_cost

    @staticmethod
    def diagnostic_cost():
        return SellConstants.DIAGNOSTIC

    def real_estate_firm_cost(self):
        if not self.simulation.use_real_estate_firm:
            return 0
        return float(self.simulation.sell_price) * SellConstants.AGENCY_FEE

    def house_price_evolution(self):
        if not self.simulation.sell_price_change:
            return 0
        return float(self.simulation.house_cost - self.simulation.sell_price)

    def monthly_expenses(self):
        if self.simulation.additional_monthly_cost is None:
            return 0
        return float(self.month * self.simulation.additional_monthly_cost)
