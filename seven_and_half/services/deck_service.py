from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, List, Union

CardValue = Union[int, float, str]

CARD_DISTRIBUTION: Dict[CardValue, int] = {
    0: 1,
    0.5: 11,
    1: 4,
    2: 4,
    3: 4,
    4: 4,
    5: 4,
    6: 4,
    7: 4,
    "Joker": 1,
}


@dataclass(frozen=True)
class Card:
    value: CardValue


@dataclass
class Deck:
    cards: List[Card]

    def draw_next_card(self) -> Card:
        if not self.cards:
            raise ValueError("Deck is empty.")
        return self.cards.pop(0)

    def remove_first_card(self, card_value: CardValue) -> None:
        for index, card in enumerate(self.cards):
            if card.value == card_value:
                del self.cards[index]
                return
        raise ValueError("Selected card not found in deck.")


class DeckService:
    def __init__(
        self,
    ) -> None:
        self._random_generator = random.Random()

    def create_shuffled_deck(self) -> Deck:
        cards = self._build_cards()
        self._shuffle_cards(cards)
        return Deck(cards=cards)

    @staticmethod
    def _build_cards() -> List[Card]:
        cards: List[Card] = []
        for value, count in CARD_DISTRIBUTION.items():
            cards.extend(Card(value=value) for _ in range(count))
        return cards

    @staticmethod
    def _shuffle_cards(cards: List[Card]) -> None:
        random.Random().shuffle(cards)
