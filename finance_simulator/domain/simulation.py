from dataclasses import dataclass

@dataclass
class Simulation:
    capital: int
    duration: int
    annual_rate: float

    @property
    def monthly_interest_rate(self):
        return 0.01 * float(self.annual_rate) / 12

    @property
    def duration_in_month(self):
        return self.duration * 12
