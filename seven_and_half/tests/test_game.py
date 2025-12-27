from seven_and_half.models.game import Game
from seven_and_half.models.hand import Hand
from seven_and_half.services.deck_service import Card, Deck, DeckService


class _StubDeckService(DeckService):
    def __init__(self, deck: Deck) -> None:
        self._deck = deck

    def create_shuffled_deck(self) -> Deck:
        return self._deck


def test_start_game_draws_one_card_each():
    deck = Deck(cards=[Card(value=1), Card(value=2), Card(value=3)])
    deck_service = _StubDeckService(deck)

    game = Game.start_game(deck_service=deck_service)

    assert [card.value for card in game.player_hand.cards] == [1]
    assert [card.value for card in game.bank_hand.cards] == [2]
    assert [card.value for card in game.deck.cards] == [3]


def test_winner_returns_bank_when_player_invalid():
    player_hand = Hand(cards=[Card(value=7), Card(value=1)])
    bank_hand = Hand(cards=[Card(value=1)])
    game = Game(player_hand=player_hand, bank_hand=bank_hand, deck=Deck(cards=[]))

    assert game.winner() == "bank"


def test_winner_returns_player_when_bank_invalid():
    player_hand = Hand(cards=[Card(value=1)])
    bank_hand = Hand(cards=[Card(value=7), Card(value=1)])
    game = Game(player_hand=player_hand, bank_hand=bank_hand, deck=Deck(cards=[]))

    assert game.winner() == "player"


def test_winner_returns_highest_value_when_both_valid():
    player_hand = Hand(cards=[Card(value=5)])
    bank_hand = Hand(cards=[Card(value=4)])
    game = Game(player_hand=player_hand, bank_hand=bank_hand, deck=Deck(cards=[]))

    assert game.winner() == "player"


def test_winner_returns_bank_on_tie():
    player_hand = Hand(cards=[Card(value=5)])
    bank_hand = Hand(cards=[Card(value=5)])
    game = Game(player_hand=player_hand, bank_hand=bank_hand, deck=Deck(cards=[]))

    assert game.winner() == "bank"
