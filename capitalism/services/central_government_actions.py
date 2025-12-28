from django.apps import apps
from django.db import models

from capitalism.models import CentralGovernment, Human, Simulation


class CentralGovernmentActionsService:
    def __init__(self, simulation: Simulation):
        self.simulation = simulation

    def run(self) -> None:
        central_government = CentralGovernment.objects.filter(simulation=self.simulation).first()
        if central_government is None:
            return

        self._distribute_funds(central_government)

    def _distribute_funds(self, central_government: CentralGovernment) -> None:
        if central_government.money <= 0:
            return

        target_job = self._get_target_job()
        if target_job is None:
            return

        humans = Human.objects.filter(dead=False, job=target_job)
        human_count = humans.count()
        if human_count == 0:
            return

        per_human_amount = central_government.money / human_count
        humans.update(money=models.F("money") + per_human_amount)
        central_government.money = 0.0
        central_government.save(update_fields=["money"])

    def _get_target_job(self):
        human_analytics_model = apps.get_model("capitalism", "HumanAnalytics")
        analytics = (
            human_analytics_model.objects.filter(day_number=self.simulation.day_number)
            .filter(number_alive__gt=0)
            .order_by("average_money")
        )
        target = analytics.first()
        if target is None:
            return None
        return target.job
