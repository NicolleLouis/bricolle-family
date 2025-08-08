from django.contrib import admin
from django.db import models


class BttdObject(models.Model):
    """An object available in Back to the Dawn."""

    name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class BttdAnimal(models.Model):
    """An animal that can desire objects."""

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class DesireStatus(models.TextChoices):
    LOVE = "love", "Love"
    LIKE = "like", "Like"
    NEUTRAL = "neutral", "Neutral"
    DISLIKE = "dislike", "Dislike"


class BttdDesire(models.Model):
    """An animal's preference for an object."""

    status = models.CharField(max_length=8, choices=DesireStatus.choices)
    animal = models.ForeignKey(BttdAnimal, on_delete=models.CASCADE, related_name="desires")
    object = models.ForeignKey(BttdObject, on_delete=models.CASCADE, related_name="desires")

    class Meta:
        unique_together = ("animal", "object")

    def __str__(self) -> str:
        return f"{self.animal} {self.status} {self.object}"


class BttdPossession(models.Model):
    """An object possessed by an animal."""

    animal = models.ForeignKey(BttdAnimal, on_delete=models.CASCADE, related_name="possessions")
    object = models.ForeignKey(BttdObject, on_delete=models.CASCADE, related_name="possessions")

    class Meta:
        unique_together = ("animal", "object")

    def __str__(self) -> str:
        return f"{self.animal} possesses {self.object}"


@admin.register(BttdObject)
class BttdObjectAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(BttdAnimal)
class BttdAnimalAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(BttdPossession)
class BttdPossessionAdmin(admin.ModelAdmin):
    list_display = ("animal", "object")
    search_fields = ("animal__name", "object__name")
    ordering = ("animal__name", "object__name")


@admin.register(BttdDesire)
class BttdDesireAdmin(admin.ModelAdmin):
    list_display = ("animal", "object", "status")
    list_filter = ("status", "object", "animal")
    search_fields = ("animal__name", "object__name")
    ordering = ("animal__name", "status")
