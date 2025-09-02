from finance_simulator.domain.amortization_month import AmortizationMonth
from finance_simulator.domain.simulation import Simulation
from finance_simulator.domain.simulation_result import SimulationResult


class SimulationService:
    def __init__(self, simulation: Simulation):
        self.simulation = simulation
        self.monthly_amount = self.compute_monthly_amount()
        self.amortizations = self.compute_amortizations()
        self.interest_reached_comparative_rent = self.compute_interest_reached_comparative_rent()
        self.total_cost_equivalent_to_rent = self.compute_total_cost_equivalent_to_rent()
        self.simulation_result = SimulationResult(
            monthly_amount=self.monthly_amount,
            amortizations=self.amortizations,
            threshold_marginal_interests_below_rent=self.interest_reached_comparative_rent,
            threshold_regular_sell_below_rent=self.total_cost_equivalent_to_rent,
        )

    def compute_monthly_amount(self):
        return round(
            float(self.simulation.capital) * self.simulation.monthly_interest_rate / (
                    1 - (1 + self.simulation.monthly_interest_rate) ** (-self.simulation.duration_in_month)),
            2
        )

    def compute_interest_reached_comparative_rent(self):
        if self.simulation.comparative_rent is None:
            return None
        for amortization in self.amortizations:
            if amortization.interests < self.simulation.comparative_rent:
                return amortization.month
        return self.simulation.duration_in_month

    def compute_total_cost_equivalent_to_rent(self):
        if self.simulation.comparative_rent is None:
            return None
        for amortization in self.amortizations:
            if amortization.net_sell_cost > 0:
                return amortization.month
        return self.simulation.duration_in_month

    def compute_amortizations(self):
        amortizations = []
        capital_remaining = float(self.simulation.capital)
        total_interest = 0
        for month_number in range(self.simulation.duration_in_month):
            amortization_month = self.generate_amortization_month(
                month_number=month_number,
                capital_remaining=capital_remaining,
                total_interest=total_interest,
            )
            capital_remaining -= amortization_month.capital_paid
            total_interest += amortization_month.interests
            amortizations.append(amortization_month)
        return amortizations

    def generate_amortization_month(self, month_number, capital_remaining, total_interest):
        interests = round(capital_remaining * self.simulation.monthly_interest_rate, 2)
        capital_paid = round(self.monthly_amount - interests, 2)
        amortization_month = AmortizationMonth(
            month=month_number,
            interests=interests,
            capital_paid=capital_paid,
            capital_remaining=round(capital_remaining, 2)
        )
        amortization_month.compute_sell_cost(
            simulation=self.simulation,
            total_interest=total_interest
        )
        return amortization_month
