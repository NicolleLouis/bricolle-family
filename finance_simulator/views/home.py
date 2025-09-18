from typing import Optional

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..constants.default_simulation import DEFAULT_SIMULATION
from ..models import Simulation
from ..forms.simulation import SimulationForm
from ..services.graph.amortization_timeseries import (
    InterestTimeseriesChart,
    NetCostTimeseriesChart,
)
from ..services.simulation import SimulationService


def _serialize_simulation(simulation: Simulation):
    return {
        "house_cost": float(simulation.house_cost),
        "initial_contribution": float(simulation.initial_contribution),
        "duration": simulation.duration,
        "annual_rate": float(simulation.annual_rate),
        "comparative_rent": float(simulation.comparative_rent)
        if simulation.comparative_rent is not None
        else None,
        "duration_before_usable": simulation.duration_before_usable,
        "use_real_estate_firm": simulation.use_real_estate_firm,
        "sell_price_change": float(simulation.sell_price_change)
        if simulation.sell_price_change is not None
        else None,
    }


def _initial_from_simulation(simulation: Simulation):
    return {
        "house_cost": simulation.house_cost,
        "initial_contribution": simulation.initial_contribution,
        "duration": simulation.duration,
        "annual_rate": simulation.annual_rate,
        "comparative_rent": simulation.comparative_rent,
        "duration_before_usable": simulation.duration_before_usable,
        "use_real_estate_firm": simulation.use_real_estate_firm,
        "sell_price_change": simulation.sell_price_change,
    }


def _get_user_simulations(request):
    if request.user.is_authenticated:
        return Simulation.objects.filter(user=request.user).order_by("name", "pk")
    return Simulation.objects.none()


def home(request, simulation: Optional[Simulation] = None):
    user_simulations = _get_user_simulations(request)
    if simulation is not None:
        request.session["simulation_data"] = _serialize_simulation(simulation)
    elif request.method == "POST":
        form = SimulationForm(request.POST)
        if form.is_valid():
            simulation = form.save(commit=False)
            request.session["simulation_data"] = _serialize_simulation(simulation)
        else:
            raise ValueError("Form is invalid")
    else:
        form = SimulationForm()
        return render(
            request,
            "finance_simulator/home.html",
            {"form": form, "user_simulations": user_simulations},
        )

    simulation_result = SimulationService(simulation).simulation_result
    interest_chart = InterestTimeseriesChart.generate(simulation_result)
    net_cost_chart = NetCostTimeseriesChart.generate(simulation_result)
    form = SimulationForm(initial=_initial_from_simulation(simulation))
    return render(
        request,
        "finance_simulator/result.html",
        {
            "simulation": simulation,
            "simulation_result": simulation_result,
            "interest_chart": interest_chart,
            "net_cost_chart": net_cost_chart,
            "form": form,
            "user_simulations": user_simulations,
        },
    )


def default_simulation(request):
    return home(request, DEFAULT_SIMULATION)


@login_required
def save_simulation(request):
    if request.method != "POST":
        return redirect("finance_simulator:home")
    name = request.POST.get("name")
    data = request.session.get("simulation_data")
    if not data or not name:
        return redirect("finance_simulator:home")
    simulation, _created = Simulation.objects.update_or_create(
        user=request.user, name=name, defaults=data
    )
    return home(request, simulation)


@login_required
def open_simulation(request, pk: int):
    simulation = get_object_or_404(Simulation, pk=pk, user=request.user)
    return home(request, simulation)
