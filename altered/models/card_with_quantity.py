from django.db import models


class CardWithQuantity(models.Model):
    card = models.ForeignKey('altered.Card', on_delete=models.CASCADE, related_name='quantities')
    deck_version = models.ForeignKey(
        'altered.DeckVersion',
        on_delete=models.CASCADE,
        related_name='card_quantities',
    )
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("card", "deck_version")

    def __str__(self):
        return f"{self.card} x{self.quantity}"
