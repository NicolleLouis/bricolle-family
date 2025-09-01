from dataclasses import dataclass
from typing import List

from finance_simulator.domain.amortization_month import AmortizationMonth


@dataclass
class SimulationResult:
    monthly_amount: float
    amortizations: List[AmortizationMonth]
