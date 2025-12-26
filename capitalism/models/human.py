from django.apps import apps
from django.contrib import admin
from django.db import models

from capitalism.constants import BASE_NEEDS
from capitalism.constants.jobs import Job
from capitalism.constants.simulation_step import (
    SimulationStep,
    DEFAULT_STEP_SEQUENCE,
)
from capitalism.services.production.service import ProductionService
from capitalism.services import HumanBuyingService, HumanSellingService


class Human(models.Model):
    DAY_STREAK_WITHOUT_NEED_LIMIT = 5
    TOTAL_DAY_WITHOUT_NEED = 30
    STEP_SEQUENCE = DEFAULT_STEP_SEQUENCE

    def _next_step_value(self):
        sequence = self.STEP_SEQUENCE
        current = SimulationStep(self.step)
        idx = sequence.index(current)
        next_idx = (idx + 1) % len(sequence)
        return sequence[next_idx]

    def next_step(self):
        next_step = self._next_step_value()
        self.step = next_step
        self.save(update_fields=["step"])
        return self.step

    def perform_current_step(self):
        match SimulationStep(self.step):
            case SimulationStep.START_OF_DAY:
                return self.perform_start_of_day()
            case SimulationStep.PRODUCTION:
                return self.perform_production()
            case SimulationStep.SELLING:
                return self.perform_selling()
            case SimulationStep.PRICE_STATS:
                return self.perform_price_stats()
            case SimulationStep.BUYING:
                return self.perform_buying()
            case SimulationStep.CONSUMPTION:
                return self.perform_consumption()
            case SimulationStep.DEATH:
                return self.perform_death()
            case SimulationStep.ANALYTICS:
                return self.perform_analytics()
            case SimulationStep.END_OF_DAY:
                return self.perform_end_of_day()
        return self.step

    name = models.CharField(max_length=128, default="", blank=True)
    age = models.IntegerField(default=0)
    job = models.CharField(
        max_length=32,
        choices=Job.choices,
        default=Job.MINER,
    )
    money = models.FloatField(default=150.0)
    time_since_need_fulfilled = models.IntegerField(default=0)
    time_without_full_needs = models.IntegerField(default=0)
    dead = models.BooleanField(default=False)
    step = models.CharField(
        max_length=32,
        choices=SimulationStep.choices,
        default=SimulationStep.START_OF_DAY,
    )

    def __str__(self):
        display_name = self.name or "Unnamed"
        return f"{display_name} - {self.get_job_display()} (age {self.age})"

    def death_check(self):
        if self.time_since_need_fulfilled > self.DAY_STREAK_WITHOUT_NEED_LIMIT:
            self.die()
        elif self.time_without_full_needs > self.TOTAL_DAY_WITHOUT_NEED:
            self.die()

    def die(self):
        self.dead = True
        self.save(update_fields=["dead"])

    def use_basic_need(self):
        needs_met = True

        for need_type, quantity in BASE_NEEDS:
            removed = self.remove_objects(need_type, quantity)
            if removed < quantity:
                needs_met = False

        if needs_met:
            self.time_since_need_fulfilled = 0
        else:
            self.time_since_need_fulfilled += 1
            self.time_without_full_needs += 1

        self.save(
            update_fields=[
                "time_since_need_fulfilled",
                "time_without_full_needs",
            ]
        )
        return needs_met

    def get_object_quantity(self, object_type: str) -> int:
        return self.owned_objects.filter(type=object_type).total_quantity()

    def has_object(self, object_type: str) -> bool:
        return self.get_object_quantity(object_type) > 0

    def add_objects(self, object_type: str, quantity: int, *, in_sale: bool = False, price=None) -> None:
        if quantity <= 0:
            return
        object_stack_model = apps.get_model("capitalism", "ObjectStack")
        stack = object_stack_model.objects.filter(
            owner=self,
            type=object_type,
            in_sale=in_sale,
            price=price,
        ).first()
        if stack:
            stack.quantity += quantity
            stack.save(update_fields=["quantity"])
            return
        object_stack_model.objects.create(
            owner=self,
            type=object_type,
            quantity=quantity,
            in_sale=in_sale,
            price=price,
        )

    def remove_objects(self, object_type: str, quantity: int) -> int:
        if quantity <= 0:
            return 0
        removed = 0
        stacks = self.owned_objects.filter(type=object_type).order_by("id")
        for stack in stacks:
            if removed >= quantity:
                break
            take = min(stack.quantity, quantity - removed)
            stack.quantity -= take
            removed += take
            if stack.quantity <= 0:
                stack.delete()
            else:
                stack.save(update_fields=["quantity"])
        return removed

    def age_a_day(self):
        self.age += 1
        self.save()

    def perform_start_of_day(self):
        return self.next_step()

    def perform_production(self):
        return ProductionService(self).run()

    def perform_selling(self):
        return HumanSellingService(self).run()

    def perform_price_stats(self):
        return self.next_step()

    def perform_buying(self):
        return HumanBuyingService(self).run()

    def perform_consumption(self):
        self.use_basic_need()
        return self.next_step()

    def perform_death(self):
        self.death_check()
        return self.next_step()

    def perform_analytics(self):
        return self.next_step()

    def perform_end_of_day(self):
        self.age_a_day()
        return self.next_step()

    @property
    def has_recently_fulfilled_basic_needs(self):
        """Return tri-state status for recent basic-need satisfaction."""
        if self.age == 0:
            return None
        if self.time_since_need_fulfilled > 0:
            return False
        return True

@admin.register(Human)
class HumanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "age",
        "job",
        "money",
        "time_since_need_fulfilled",
        "time_without_full_needs",
        "dead",
        "step",
    )
    list_filter = ("job", "step", "dead")
    search_fields = ("name", "job")
