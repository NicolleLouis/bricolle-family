from django.contrib import admin
from django.db import models


class CentralGovernment(models.Model):
    simulation = models.OneToOneField(
        "capitalism.Simulation",
        on_delete=models.CASCADE,
        related_name="central_government",
    )
    money = models.FloatField(default=0.0)
    lifetime_collected_money = models.FloatField(default=0.0)

    def __str__(self):
        return f"Central Government (simulation {self.simulation_id})"

    def receive_money(self, amount: float) -> None:
        if amount <= 0:
            return
        self.money += amount
        self.lifetime_collected_money += amount
        self.save(update_fields=["money", "lifetime_collected_money"])


@admin.register(CentralGovernment)
class CentralGovernmentAdmin(admin.ModelAdmin):
    list_display = ("id", "simulation", "money", "lifetime_collected_money")
