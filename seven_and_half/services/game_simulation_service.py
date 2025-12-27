from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from seven_and_half.models.hand import Hand
from seven_and_half.services.deck_service import Card, CardValue, DeckService, CARD_DISTRIBUTION, Deck

DEFAULT_SIMULATION_COUNT = 1000


@dataclass(frozen=True)
class GameSimulationResult:
    simulations: int
    player_wins: int
    bank_wins: int
    player_win_rate: float


class GameSimulationService:
    def simulate_games(
        self,
        player_card_value: CardValue | None,
        bank_card_value: CardValue | None,
        simulations: int = DEFAULT_SIMULATION_COUNT,
    ) -> GameSimulationResult:
        player_wins = 0
        bank_wins = 0

        for _ in range(simulations):
            deck = DeckService().create_shuffled_deck()
            player_hand = Hand()
            bank_hand = Hand()

            if player_card_value is None and bank_card_value is None:
                player_hand.add_card(deck.draw_next_card())
                bank_hand.add_card(deck.draw_next_card())
            elif player_card_value is None:
                deck.remove_first_card(bank_card_value)
                bank_hand.add_card(Card(value=bank_card_value))
                player_hand.add_card(deck.draw_next_card())
            elif bank_card_value is None:
                deck.remove_first_card(player_card_value)
                player_hand.add_card(Card(value=player_card_value))
                bank_hand.add_card(deck.draw_next_card())
            else:
                deck.remove_first_card(player_card_value)
                deck.remove_first_card(bank_card_value)
                player_hand.add_card(Card(value=player_card_value))
                bank_hand.add_card(Card(value=bank_card_value))

            self._play_player_turn(player_hand, bank_hand, deck)
            if not player_hand.valid:
                bank_wins += 1
                continue

            self._play_bank_turn(bank_hand, player_hand, deck)
            if not bank_hand.valid:
                player_wins += 1
                continue

            if player_hand.value() > bank_hand.value():
                player_wins += 1
            else:
                bank_wins += 1

        player_win_rate = player_wins / simulations if simulations else 0.0

        return GameSimulationResult(
            simulations=simulations,
            player_wins=player_wins,
            bank_wins=bank_wins,
            player_win_rate=player_win_rate,
        )

    @staticmethod
    def validate_initial_cards(
        player_card_value: CardValue | None, bank_card_value: CardValue | None
    ) -> bool:
        required_counts: Dict[CardValue, int] = {}
        if player_card_value is not None:
            required_counts[player_card_value] = 1
        if bank_card_value is not None:
            required_counts[bank_card_value] = required_counts.get(bank_card_value, 0) + 1

        for value, required in required_counts.items():
            available = CARD_DISTRIBUTION.get(value, 0)
            if required > available:
                return False
        return True

    @staticmethod
    def _play_player_turn(player_hand: Hand, bank_hand: Hand, deck: Deck) -> None:
        while player_hand.valid and (
            player_hand.value() <= bank_hand.value() or player_hand.value() < 5.5
        ):
            if not deck.cards:
                return
            player_hand.add_card(deck.draw_next_card())

    @staticmethod
    def _play_bank_turn(bank_hand: Hand, player_hand: Hand, deck: Deck) -> None:
        while bank_hand.valid and bank_hand.value() < player_hand.value():
            if not deck.cards:
                return
            bank_hand.add_card(deck.draw_next_card())
