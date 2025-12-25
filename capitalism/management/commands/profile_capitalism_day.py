from __future__ import annotations

from django.core.management.base import BaseCommand

from capitalism.models import Simulation
from capitalism.services.profiling.day_profiler import SimulationDayProfilerService


class Command(BaseCommand):
    help = "Profile one simulation day and report per-step duration and query count."

    def add_arguments(self, parser):
        parser.add_argument(
            "--simulation-id",
            type=int,
            dest="simulation_id",
            help="Simulation id to profile (defaults to the first simulation).",
        )

    def handle(self, *args, **options):
        simulation_id = options.get("simulation_id")
        if simulation_id is None:
            simulation = Simulation.objects.order_by("id").first()
        else:
            simulation = Simulation.objects.filter(id=simulation_id).first()

        if simulation is None:
            self.stderr.write("No simulation found to profile.")
            return

        self.stdout.write(
            "Profiling one day (note: this advances the simulation state)."
        )
        results = SimulationDayProfilerService(simulation).run()
        for entry in results:
            self.stdout.write(
                f"{entry['step']:<15} {entry['duration_milliseconds']:.2f} ms"
                f"  {entry['queries']} queries"
            )
