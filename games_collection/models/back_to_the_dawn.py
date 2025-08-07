from django.db import models


class BttdObject(models.Model):
    """An object available in Back to the Dawn."""

    name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.name


class BttdAnimal(models.Model):
    """An animal that can desire objects."""

    name = models.CharField(max_length=100)

    def __str__(self) -> str:  # pragma: no cover - simple representation
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

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.animal} {self.status} {self.object}"
