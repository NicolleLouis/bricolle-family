from typing import Optional

from django.shortcuts import render

from ..constants.default_simulation import DEFAULT_SIMULATION
from ..domain.simulation import Simulation
from ..forms.simulation import SimulationForm
from ..services.graph.amortization_timeseries import InterestTimeseriesChart, NetCostTimeseriesChart
from ..services.simulation import SimulationService


def home(request, simulation: Optional[Simulation] = None):
    if request.method == "POST"or simulation is not None:
        if simulation is None:
            form = SimulationForm(request.POST)
            if form.is_valid():
                simulation = Simulation(
                    house_cost=form.cleaned_data.get("house_cost"),
                    initial_contribution=form.cleaned_data.get("initial_contribution"),
                    duration=form.cleaned_data.get("years"),
                    annual_rate=form.cleaned_data.get("rate"),
                    comparative_rent=form.cleaned_data.get("comparative_rent"),
                    duration_before_usable=form.cleaned_data.get("duration_before_usable"),
                    use_real_estate_firm=form.cleaned_data.get("use_real_estate_firm"),
                )
            else:
                raise ValueError("Form is invalid")
        simulation_result = SimulationService(simulation).simulation_result
        interest_chart = InterestTimeseriesChart.generate(simulation_result)
        net_cost_chart = NetCostTimeseriesChart.generate(simulation_result)
        form = SimulationForm(
            initial={
                "house_cost": simulation.house_cost,
                "initial_contribution": simulation.initial_contribution,
                "years": simulation.duration,
                "rate": simulation.annual_rate,
                "comparative_rent": simulation.comparative_rent,
                "duration_before_usable": simulation.duration_before_usable,
                "use_real_estate_firm": simulation.use_real_estate_firm,
            }
        )
        return render(
            request,
            "finance_simulator/result.html",
            {
                "simulation": simulation,
                "simulation_result": simulation_result,
                "interest_chart": interest_chart,
                "net_cost_chart": net_cost_chart,
                "form": form,
            },
        )
    else:
        form = SimulationForm()
    return render(request, "finance_simulator/home.html", {"form": form})


def default_simulation(request):
    return home(request, DEFAULT_SIMULATION)
