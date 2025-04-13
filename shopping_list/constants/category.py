from django.db import models


class Category(models.TextChoices):
    DAIRY = "DAIRY", "Dairy"
    FISH = "FISH", "Fish"
    FRUIT = "FRUIT", "Fruit"
    GRAINS = "GRAINS", "Grains"
    MEAT = "MEAT", "Meat"
    NON_EDIBLE = "NON_EDIBLE", "Non Edible"
    SPICE = "SPICE", "Spice"
    SWEET = "SWEET", "Sweet"
    VEGETABLE = "VEGETABLE", "Vegetable"
