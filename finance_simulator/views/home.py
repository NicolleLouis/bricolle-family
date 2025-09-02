from django.shortcuts import render

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
                comparative_rent=form.cleaned_data.get("comparative_rent"),
            )
            simulation_result = SimulationService(simulation).simulation_result
            interest_chart = InterestTimeseriesChart.generate(simulation_result)
            return render(
                request,
                "finance_simulator/result.html",
                {
                    "simulation": simulation,
                    "simulation_result": simulation_result,
                    "interest_chart": interest_chart,
                },
            )
    else:
        form = SimulationForm()
    return render(request, "finance_simulator/home.html", {"form": form})
