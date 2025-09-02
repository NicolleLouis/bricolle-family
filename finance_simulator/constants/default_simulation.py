from finance_simulator.domain.simulation import Simulation

DEFAULT_SIMULATION = Simulation(
    house_cost=480000,
    initial_contribution=100000,
    duration=20,
    annual_rate=3.09,
    comparative_rent=1600,
    duration_before_usable=21,
)
