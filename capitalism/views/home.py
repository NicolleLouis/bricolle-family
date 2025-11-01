from django.contrib import messages
from django.shortcuts import redirect, render

from capitalism.models import Simulation
from capitalism.services.dashboard import DashboardService


class HomeView:
    @staticmethod
    def home(request):
        if request.method == "POST":
            action = request.POST.get("action")
            if action == "next_day":
                return HomeView._next_day(request)
            if action == "next_step":
                return HomeView._next_step(request)

        macro_info = DashboardService().macro_overview()
        return render(request, "capitalism/home.html", {"macro_info": macro_info})

    @staticmethod
    def _next_step(request):
        simulation = Simulation.objects.order_by("id").first()
        if simulation is None:
            messages.error(request, "Aucune simulation disponible.")
            return redirect("capitalism:home")

        try:
            simulation.finish_current_step()
        except Exception as exc:  # pylint: disable=broad-except
            messages.error(
                request,
                f"Erreur lors de l'exécution de la prochaine étape : {exc}",
            )
        else:
            messages.success(
                request,
                f"Étape suivante exécutée : {simulation.get_step_display()}.",
            )
        return redirect("capitalism:home")

    @staticmethod
    def _next_day(request):
        simulation = Simulation.objects.order_by("id").first()
        if simulation is None:
            messages.error(request, "Aucune simulation disponible.")
            return redirect("capitalism:home")

        try:
            simulation.next_day()
        except Exception as exc:  # pylint: disable=broad-except
            messages.error(
                request,
                f"Erreur lors de l'exécution de la journée complète : {exc}",
            )
        else:
            messages.success(
                request,
                "Journée complète exécutée avec succès.",
            )
        return redirect("capitalism:home")
