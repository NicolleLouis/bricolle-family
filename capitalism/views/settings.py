from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from capitalism.services.human_factory import HumanFactory

from capitalism.constants.jobs import Job
from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import (
    Human,
    HumanAnalytics,
    Object,
    Simulation,
    Transaction,
)


class SettingView:
    template_name = "capitalism/settings.html"

    @staticmethod
    def home(request):
        if request.method == "POST":
            action = request.POST.get("action")
            if action == "start":
                return SettingView._start_simulation(request)
            if action == "reset":
                return SettingView._reset_simulation(request)
            if action == "generate":
                return SettingView._generate_humans(request)

        simulation = Simulation.objects.order_by("id").first()
        return render(
            request,
            SettingView.template_name,
            {
                "simulation": simulation,
                "jobs": Job.choices,
            },
        )

    @staticmethod
    def _ensure_simulation():
        simulation = Simulation.objects.order_by("id").first()
        if simulation is None:
            simulation = Simulation.objects.create()
        return simulation

    @staticmethod
    def _start_simulation(request):
        simulation = SettingView._ensure_simulation()
        messages.success(
            request,
            f"Simulation prête (jour {simulation.day_number}, étape {simulation.get_step_display()}).",
        )
        return redirect("capitalism:settings")

    @staticmethod
    def _reset_simulation(request):
        with transaction.atomic():
            Human.objects.all().delete()
            Object.objects.all().delete()
            HumanAnalytics.objects.all().delete()
            Transaction.objects.all().delete()
            Simulation.objects.all().delete()
            simulation = Simulation.objects.create()

        messages.warning(
            request,
            f"Simulation réinitialisée (jour {simulation.day_number}, étape {simulation.get_step_display()}).",
        )
        return redirect("capitalism:settings")

    @staticmethod
    def _generate_humans(request):
        simulation = SettingView._ensure_simulation()
        if simulation.step != SimulationStep.START_OF_DAY:
            messages.error(
                request,
                "Impossible de générer des humains si la simulation n'est pas sur Start of Day.",
            )
            return redirect("capitalism:settings")

        created = 0
        for job_value, _ in Job.choices:
            raw_amount = request.POST.get(f"count_{job_value}", "").strip()
            if not raw_amount:
                continue
            try:
                amount = int(raw_amount)
            except ValueError:
                messages.error(request, f"Valeur invalide pour {job_value}: {raw_amount}")
                return redirect("capitalism:settings")

            if amount < 0:
                messages.error(request, f"Le nombre ne peut pas être négatif pour {job_value}.")
                return redirect("capitalism:settings")

            HumanFactory.bulk_create(job_value, amount)
            created += amount

        messages.success(request, f"{created} humains ajoutés.")
        return redirect("capitalism:settings")
