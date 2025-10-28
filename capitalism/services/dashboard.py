from typing import Any, Dict

from capitalism.models import Human, Simulation


class DashboardService:
    """Compute aggregated information displayed on the home dashboard."""

    def macro_overview(self) -> Dict[str, Any]:
        simulation = Simulation.objects.order_by("id").first()
        alive_humans = Human.objects.filter(dead=False).count()

        if simulation is None:
            return {
                "has_simulation": False,
                "day_number": None,
                "step": None,
                "step_label": None,
                "alive_humans": alive_humans,
            }

        return {
            "has_simulation": True,
            "day_number": simulation.day_number,
            "step": simulation.step,
            "step_label": simulation.get_step_display(),
            "alive_humans": alive_humans,
        }
