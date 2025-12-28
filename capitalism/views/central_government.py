from django.contrib import messages
from django.shortcuts import render

from capitalism.models import CentralGovernment, Simulation


class CentralGovernmentView:
    template_name = "capitalism/central_government.html"

    @staticmethod
    def home(request):
        simulation = Simulation.objects.order_by("id").first()
        if simulation is None:
            messages.error(request, "Aucune simulation disponible.")
            return render(
                request,
                CentralGovernmentView.template_name,
                {"simulation": None, "central_government": None},
            )

        central_government, _ = CentralGovernment.objects.get_or_create(
            simulation=simulation
        )

        return render(
            request,
            CentralGovernmentView.template_name,
            {
                "simulation": simulation,
                "central_government": central_government,
            },
        )
