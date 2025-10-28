from django.db import models


class ObjectType(models.TextChoices):
    ORE = "ore", "Ore"
    WOOD = "wood", "Wood"
    WHEAT = "wheat", "Wheat"
    FLOUR = "flour", "Flour"
    BREAD = "bread", "Bread"
    PICKAXE = "pickaxe", "Pickaxe"
    AXE = "axe", "Axe"
    SCYTHE = "scythe", "Scythe"
    SPATULA = "spatula", "Spatula"
