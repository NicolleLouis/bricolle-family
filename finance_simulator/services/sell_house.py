from __future__ import annotations

from finance_simulator.constants.sell import SellConstants
from finance_simulator.domain.simulation import Simulation

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from finance_simulator.domain.amortization_month import AmortizationMonth



class SellHouseService:
    def __init__(self, simulation: Simulation, amortization_month: AmortizationMonth):
        self.simulation = simulation
        self.amortization_month = amortization_month

    def compute_sell_cost(self):
        sell_cost = 0
        sell_cost += self.diagnostic_cost()
        sell_cost += self.real_estate_firm_cost()
        sell_cost += self.house_price_evolution()
        return sell_cost

    @staticmethod
    def diagnostic_cost():
        return SellConstants.DIAGNOSTIC

    def real_estate_firm_cost(self):
        if not self.simulation.use_real_estate_firm:
            return 0
        return float(self.simulation.house_cost) * SellConstants.AGENCY_FEE

    def house_price_evolution(self):
        if not self.simulation.sell_price_change:
            return 0
        return float(self.simulation.house_cost - self.simulation.sell_price)
