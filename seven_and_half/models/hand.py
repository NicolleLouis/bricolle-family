from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from seven_and_half.services.deck_service import Card


@dataclass
class Hand:
    cards: List[Card] = field(default_factory=list)

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def value(self) -> float:
        base_total = 0.0
        joker_count = 0

        for card in self.cards:
            if card.value == "Joker":
                joker_count += 1
            else:
                base_total += float(card.value)

        if joker_count == 0:
            return base_total

        possible_totals = {base_total}
        for _ in range(joker_count):
            next_totals = set()
            for total in possible_totals:
                for joker_value in range(1, 8):
                    next_totals.add(total + joker_value)
            possible_totals = next_totals

        valid_totals = [total for total in possible_totals if total <= 7.5]
        if valid_totals:
            return max(valid_totals)

        return base_total + joker_count

    @property
    def valid(self) -> bool:
        return self.value() <= 7.5
