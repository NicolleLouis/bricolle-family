from django.db import models


class Archetype(models.TextChoices):
    FIXER_UPPER = "FIXER_UPPER", "Fixer Upper"
    SINGLE_WEAPON = "SINGLE_WEAPON", "Single Weapon"
    PUFFERFISH = "PUFFERFISH", "Pufferfish"
    LIGHTHOUSE_BURN = "LIGHTHOUSE_BURN", "Lighthouse Burn"
    DOUBLE_WHAMMY = "DOUBLE_WHAMMY", "Double Whammy"
    POWER_DRILL = "POWER_DRILL", "Power Drill"
    SPIDER_MACE = "SPIDER_MACE", "Spider Mace"
    BOTTLED_EXPLOSION = "BOTTLED_EXPLOSION", "Bottled Explosion"
    ACID_VAT = "ACID_VAT", "Vat of Acid"