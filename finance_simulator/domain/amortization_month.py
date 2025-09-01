from dataclasses import dataclass

@dataclass
class AmortizationMonth:
    month: int
    interests: float
    capital_paid: float
    capital_remaining: float
