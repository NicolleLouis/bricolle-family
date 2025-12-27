from seven_and_half.models.hand import Hand
from seven_and_half.services.deck_service import Card


def test_add_card_adds_to_hand():
    hand = Hand()

    hand.add_card(Card(value=2))

    assert [card.value for card in hand.cards] == [2]


def test_value_sums_numeric_cards():
    hand = Hand(cards=[Card(value=1), Card(value=0.5), Card(value=3)])

    assert hand.value() == 4.5


def test_value_uses_best_joker_value_under_limit():
    hand = Hand(cards=[Card(value=5), Card(value="Joker")])

    assert hand.value() == 7.0


def test_value_optimizes_multiple_jokers():
    hand = Hand(cards=[Card(value=3), Card(value="Joker"), Card(value="Joker")])

    assert hand.value() == 7.0


def test_value_defaults_joker_to_one_when_over_limit():
    hand = Hand(cards=[Card(value=7), Card(value=0.5), Card(value="Joker")])

    assert hand.value() == 8.5


def test_valid_returns_true_when_under_limit():
    hand = Hand(cards=[Card(value=7), Card(value=0.5)])

    assert hand.valid is True


def test_valid_returns_false_when_over_limit():
    hand = Hand(cards=[Card(value=7), Card(value=0.5), Card(value=1)])

    assert hand.valid is False
