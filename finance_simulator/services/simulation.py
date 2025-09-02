from finance_simulator.domain.amortization_month import AmortizationMonth
from finance_simulator.domain.simulation import Simulation
from finance_simulator.domain.simulation_result import SimulationResult


class SimulationService:
    def __init__(self, simulation: Simulation):
        self.simulation = simulation
        self.monthly_amount = self.compute_monthly_amount()
        self.interest_reached_comparative_rent = None
        self.amortizations = self.compute_amortizations()
        self.simulation_result = SimulationResult(
            monthly_amount=self.monthly_amount,
            amortizations=self.amortizations,
            threshold_interests_below_rent=self.interest_reached_comparative_rent,
        )

    def compute_monthly_amount(self):
        return round(
            float(self.simulation.capital) * self.simulation.monthly_interest_rate / (
                    1 - (1 + self.simulation.monthly_interest_rate) ** (-self.simulation.duration_in_month)),
            2
        )

    def compute_amortizations(self):
        amortizations = []
        capital_remaining = float(self.simulation.capital)
        for month_number in range(self.simulation.duration_in_month):
            interests = round(capital_remaining * self.simulation.monthly_interest_rate, 2)
            if self.interest_reached_comparative_rent is None:
                if interests < self.simulation.comparative_rent:
                    self.interest_reached_comparative_rent = month_number
            capital_paid = round(self.monthly_amount - interests, 2)
            capital_remaining -= capital_paid
            amortization_month = AmortizationMonth(
                month=month_number,
                interests=interests,
                capital_paid=capital_paid,
                capital_remaining=round(capital_remaining, 2)
            )
            amortizations.append(amortization_month)
        return amortizations
