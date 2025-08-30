from django.shortcuts import render

from ..forms import SimulationForm


def home(request):
    if request.method == "POST":
        form = SimulationForm(request.POST)
        if form.is_valid():
            return render(request, "finance_simulator/result.html", form.cleaned_data)
    else:
        form = SimulationForm()
    return render(request, "finance_simulator/home.html", {"form": form})
