from __future__ import annotations

from dataclasses import dataclass

from seven_and_half.models.hand import Hand
from seven_and_half.services.deck_service import Deck, DeckService


@dataclass
class Game:
    player_hand: Hand
    bank_hand: Hand
    deck: Deck

    @classmethod
    def start_game(cls, deck_service: DeckService | None = None) -> "Game":
        service = deck_service or DeckService()
        deck = service.create_shuffled_deck()
        player_hand = Hand()
        bank_hand = Hand()

        player_hand.add_card(deck.draw_next_card())
        bank_hand.add_card(deck.draw_next_card())

        return cls(player_hand=player_hand, bank_hand=bank_hand, deck=deck)

    def winner(self) -> str:
        if not self.player_hand.valid:
            return "bank"
        if not self.bank_hand.valid:
            return "player"
        if self.player_hand.value() > self.bank_hand.value():
            return "player"
        return "bank"
