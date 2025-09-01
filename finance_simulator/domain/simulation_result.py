from dataclasses import dataclass
from typing import List

from finance_simulator.domain.amortization_month import AmortizationMonth


@dataclass
class SimulationResult:
    monthly_amount: float
    amortizations: List[AmortizationMonth]

    @property
    def total_interest_amount(self):
        total_amount = 0
        for amortization in self.amortizations:
            total_amount += amortization.interests
        return round(total_amount, 2)
