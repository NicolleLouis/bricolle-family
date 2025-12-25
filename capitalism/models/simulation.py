import random

from django.contrib import admin
from django.db import models
from capitalism.constants.simulation_step import (
    SimulationStep,
    DEFAULT_STEP_SEQUENCE,
)
from capitalism.models import Human
from capitalism.services.human_analytics import HumanAnalyticsRecorderService
from capitalism.services.pricing import TransactionPriceAnalyticsService


class Simulation(models.Model):
    class SimulationStepBlockedError(RuntimeError):
        """Raised when the simulation cannot advance to the next step."""

    class InvalidHumanStepError(RuntimeError):
        """Raised when humans are not on the expected step during simulation progression."""

    STEP_SEQUENCE = DEFAULT_STEP_SEQUENCE

    def _next_step_value(self):
        sequence = self.STEP_SEQUENCE
        current = SimulationStep(self.step)
        idx = sequence.index(current)
        next_idx = (idx + 1) % len(sequence)
        return sequence[next_idx]

    day_number = models.IntegerField(default=0)
    step = models.CharField(
        max_length=32,
        choices=SimulationStep.choices,
        default=SimulationStep.START_OF_DAY,
    )

    def __str__(self):
        return f"Day {self.day_number} - {self.get_step_display()}"

    def next_step(self):
        if not self.can_change_step():
            current = SimulationStep(self.step)
            raise self.SimulationStepBlockedError(
                f"Impossible d'avancer la simulation depuis l'étape {current.label}."
            )

        sequence = self.STEP_SEQUENCE
        current = SimulationStep(self.step)
        idx = sequence.index(current)
        next_idx = (idx + 1) % len(sequence)
        new_step = sequence[next_idx]

        update_fields = ["step"]
        if current == SimulationStep.END_OF_DAY and new_step == SimulationStep.START_OF_DAY:
            self.day_number += 1
            update_fields.append("day_number")

        self.step = new_step
        self.save(update_fields=update_fields)
        return self.step

    def can_change_step(self):
        self._validate_human_steps()

        match SimulationStep(self.step):
            case SimulationStep.START_OF_DAY:
                return self.can_change_step_start_of_day()
            case SimulationStep.PRODUCTION:
                return self.can_change_step_production()
            case SimulationStep.SELLING:
                return self.can_change_step_selling()
            case SimulationStep.PRICE_STATS:
                return self.can_change_step_price_stats()
            case SimulationStep.BUYING:
                return self.can_change_step_buying()
            case SimulationStep.CONSUMPTION:
                return self.can_change_step_consumption()
            case SimulationStep.DEATH:
                return self.can_change_step_death()
            case SimulationStep.ANALYTICS:
                return self.can_change_step_analytics()
            case SimulationStep.END_OF_DAY:
                return self.can_change_step_end_of_day()
        return False

    def finish_current_step(self):
        self._validate_human_steps()

        match SimulationStep(self.step):
            case SimulationStep.START_OF_DAY:
                return self.finish_current_step_start_of_day()
            case SimulationStep.PRODUCTION:
                return self.finish_current_step_production()
            case SimulationStep.SELLING:
                return self.finish_current_step_selling()
            case SimulationStep.PRICE_STATS:
                return self.finish_current_step_price_stats()
            case SimulationStep.BUYING:
                return self.finish_current_step_buying()
            case SimulationStep.CONSUMPTION:
                return self.finish_current_step_consumption()
            case SimulationStep.DEATH:
                return self.finish_current_step_death()
            case SimulationStep.ANALYTICS:
                return self.finish_current_step_analytics()
            case SimulationStep.END_OF_DAY:
                return self.finish_current_step_end_of_day()
        return self.step

    # Helpers -------------------------------------------------
    def _validate_human_steps(self):
        current_step = SimulationStep(self.step)
        next_step = self._next_step_value()
        allowed_values = {current_step.value, next_step.value}

        alive_humans = Human.objects.filter(dead=False, step__isnull=False)
        invalid_steps = (
            alive_humans.exclude(step__in=allowed_values)
            .values_list("step", flat=True)
            .distinct()
        )

        if invalid_steps:
            labels = ", ".join(
                sorted(SimulationStep(step).label for step in invalid_steps if step)
            )
            raise self.InvalidHumanStepError(
                f"Humans are on invalid steps for {self.step}: {labels}."
            )

    # Step-specific hooks -------------------------------------------------
    def can_change_step_start_of_day(self):
        return True

    def can_change_step_production(self):
        return True

    def can_change_step_selling(self):
        return True

    def can_change_step_price_stats(self):
        from capitalism.constants.object_type import ObjectType
        from capitalism.models import PriceAnalytics

        day_number = self.day_number
        analytics_types = set(
            PriceAnalytics.objects.filter(day_number=day_number).values_list(
                "object_type", flat=True
            )
        )
        expected_types = {choice for choice, _label in ObjectType.choices}
        return expected_types.issubset(analytics_types)

    def can_change_step_buying(self):
        return True

    def can_change_step_consumption(self):
        return True

    def can_change_step_death(self):
        return True

    def can_change_step_analytics(self):
        from capitalism.constants.jobs import Job
        from capitalism.models import HumanAnalytics, Transaction

        day_number = self.day_number
        recorded_jobs = set(
            HumanAnalytics.objects.filter(day_number=day_number).values_list("job", flat=True)
        )
        expected_jobs = {choice for choice, _label in Job.choices}
        return expected_jobs.issubset(recorded_jobs) and not Transaction.objects.exists()

    def can_change_step_end_of_day(self):
        return True

    def finish_current_step_start_of_day(self):
        starters = Human.objects.filter(dead=False, step=SimulationStep.START_OF_DAY)
        for human in starters:
            human.perform_current_step()

        return self.next_step()

    def finish_current_step_production(self):
        producers = Human.objects.filter(dead=False, step=SimulationStep.PRODUCTION)
        for human in producers:
            human.perform_current_step()

        return self.next_step()

    def finish_current_step_selling(self):
        sellers = Human.objects.filter(dead=False, step=SimulationStep.SELLING)
        for human in sellers:
            human.perform_current_step()

        return self.next_step()

    def finish_current_step_price_stats(self):
        from capitalism.services.pricing import PriceAnalyticsRecorderService

        PriceAnalyticsRecorderService(day_number=self.day_number).run()

        humans = Human.objects.filter(dead=False, step=SimulationStep.PRICE_STATS)
        for human in humans:
            human.perform_current_step()

        return self.next_step()

    def finish_current_step_buying(self):
        buyers = list(
            Human.objects.filter(dead=False, step=SimulationStep.BUYING).order_by("id")
        )
        random.shuffle(buyers)
        for human in buyers:
            human.perform_current_step()

        return self.next_step()

    def finish_current_step_consumption(self):
        consumers = Human.objects.filter(dead=False, step=SimulationStep.CONSUMPTION)
        for human in consumers:
            human.perform_current_step()

        return self.next_step()

    def finish_current_step_death(self):
        humans = Human.objects.filter(dead=False, step=SimulationStep.DEATH)
        for human in humans:
            human.perform_current_step()

        return self.next_step()

    def finish_current_step_analytics(self):
        HumanAnalyticsRecorderService(day_number=self.day_number).run()
        TransactionPriceAnalyticsService(day_number=self.day_number).run()

        humans = Human.objects.filter(dead=False, step=SimulationStep.ANALYTICS)
        for human in humans:
            human.perform_current_step()

        return self.next_step()

    def finish_current_step_end_of_day(self):
        from capitalism.models import Human, Object
        from capitalism.services.pricing import MarketPerceivedPriceUpdateService

        Human.objects.filter(dead=True).delete()

        Object.objects.update(price=None, in_sale=False)

        survivors = Human.objects.filter(dead=False, step=SimulationStep.END_OF_DAY)
        for human in survivors:
            human.perform_current_step()

        MarketPerceivedPriceUpdateService(day_number=self.day_number).update()

        return self.next_step()

    def next_day(self):
        for _ in range(len(self.STEP_SEQUENCE)):
            new_step = self.finish_current_step()
            if new_step == SimulationStep.START_OF_DAY:
                return new_step

        return SimulationStep(self.step)



@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    list_display = ("id", "day_number", "step")
    list_filter = ("step",)
