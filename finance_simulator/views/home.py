from django.shortcuts import render

from ..constants.default_simulation import DEFAULT_SIMULATION
from ..domain.simulation import Simulation
from ..forms.simulation import SimulationForm
from ..services.graph.interest_timeseries import InterestTimeseriesChart
from ..services.simulation import SimulationService


def home(request):
    if request.method == "POST":
        form = SimulationForm(request.POST)
        if form.is_valid():
            simulation = Simulation(
                capital=form.cleaned_data.get("capital"),
                duration=form.cleaned_data.get("years"),
                annual_rate=form.cleaned_data.get("rate"),
                comparative_rent=form.cleaned_data.get("comparative_rent") or 0,
            )
            simulation_result = SimulationService(simulation).simulation_result
            interest_chart = InterestTimeseriesChart.generate(simulation_result)
            form = SimulationForm(
                initial={
                    "capital": simulation.capital,
                    "years": simulation.duration,
                    "rate": simulation.annual_rate,
                    "comparative_rent": simulation.comparative_rent,
                }
            )
            return render(
                request,
                "finance_simulator/result.html",
                {
                    "simulation": simulation,
                    "simulation_result": simulation_result,
                    "interest_chart": interest_chart,
                    "form": form,
                },
            )
    else:
        form = SimulationForm()
    return render(request, "finance_simulator/home.html", {"form": form})


def default_simulation(request):
    simulation = DEFAULT_SIMULATION
    simulation_result = SimulationService(simulation).simulation_result
    interest_chart = InterestTimeseriesChart.generate(simulation_result)
    form = SimulationForm(
        initial={
            "capital": simulation.capital,
            "years": simulation.duration,
            "rate": simulation.annual_rate,
            "comparative_rent": simulation.comparative_rent,
        }
    )
    return render(
        request,
        "finance_simulator/result.html",
        {
            "simulation": simulation,
            "simulation_result": simulation_result,
            "interest_chart": interest_chart,
            "form": form,
        },
    )
