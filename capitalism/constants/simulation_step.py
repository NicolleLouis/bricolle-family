from django.db import models


class SimulationStep(models.TextChoices):
    START_OF_DAY = "start_of_day", "Start of Day"
    PRODUCTION = "production", "Production"
    SELLING = "selling", "Selling"
    PRICE_STATS = "price_stats", "Price Statistics"
    BUYING = "buying", "Buying"
    CONSUMPTION = "consumption", "Consumption"
    DEATH = "death", "Death"
    ANALYTICS = "analytics", "Analytics"
    GOVERNMENT_ACTIONS = "government_actions", "Government Actions"
    END_OF_DAY = "end_of_day", "End of Day"


DEFAULT_STEP_SEQUENCE = (
    SimulationStep.START_OF_DAY,
    SimulationStep.PRODUCTION,
    SimulationStep.SELLING,
    SimulationStep.PRICE_STATS,
    SimulationStep.BUYING,
    SimulationStep.CONSUMPTION,
    SimulationStep.DEATH,
    SimulationStep.ANALYTICS,
    SimulationStep.GOVERNMENT_ACTIONS,
    SimulationStep.END_OF_DAY,
)
