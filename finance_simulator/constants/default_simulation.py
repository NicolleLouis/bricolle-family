from finance_simulator.constants.notary_fee import NotaryFeesOption
from finance_simulator.models import Simulation

DEFAULT_SIMULATION = Simulation(
    house_cost=552000,
    initial_contribution=112472,
    duration=20,
    annual_rate=3.09,
    comparative_rent=2000,
    duration_before_usable=0,
    notary_fees=NotaryFeesOption.NO,
    sell_price_change=0,
    monthly_expenses=375,
    property_tax=2000,
)
