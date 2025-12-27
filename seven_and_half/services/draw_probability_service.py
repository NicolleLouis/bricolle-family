from __future__ import annotations

from dataclasses import dataclass
from typing import List

from seven_and_half.models.hand import Hand
from seven_and_half.services.deck_service import Card, CardValue, DeckService


@dataclass(frozen=True)
class DrawProbabilityResult:
    bust_probability: float
    success_probability: float
    bust_cards: int
    total_cards: int


class DrawProbabilityService:
    def __init__(self, deck_service: DeckService | None = None) -> None:
        self._deck_service = deck_service or DeckService()

    def calculate_draw_probabilities(self, initial_card_value: CardValue) -> DrawProbabilityResult:
        deck = self._deck_service.create_shuffled_deck()
        deck.remove_first_card(initial_card_value)

        total_cards = len(deck.cards)
        if total_cards == 0:
            return DrawProbabilityResult(
                bust_probability=0.0,
                success_probability=0.0,
                bust_cards=0,
                total_cards=0,
            )

        bust_cards = self._count_bust_cards(initial_card_value, deck.cards)
        bust_probability = bust_cards / total_cards
        success_probability = 1 - bust_probability

        return DrawProbabilityResult(
            bust_probability=bust_probability,
            success_probability=success_probability,
            bust_cards=bust_cards,
            total_cards=total_cards,
        )

    @staticmethod
    def _count_bust_cards(initial_card_value: CardValue, remaining_cards: List[Card]) -> int:
        bust_cards = 0
        for card in remaining_cards:
            hand = Hand(cards=[Card(value=initial_card_value), card])
            if not hand.valid:
                bust_cards += 1
        return bust_cards
