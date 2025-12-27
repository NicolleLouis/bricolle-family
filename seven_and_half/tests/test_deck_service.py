from collections import Counter

import pytest

from seven_and_half.services.deck_service import (
    Card,
    Deck,
    DeckService,
    CARD_DISTRIBUTION,
)


def test_create_shuffled_deck_has_expected_distribution():
    deck_service = DeckService()

    deck = deck_service.create_shuffled_deck()

    counts = Counter(card.value for card in deck.cards)
    assert counts == CARD_DISTRIBUTION


def test_draw_next_card_removes_card_from_deck():
    deck = Deck(cards=[Card(value=1), Card(value=2)])

    first_card = deck.draw_next_card()

    assert first_card.value == 1
    assert [card.value for card in deck.cards] == [2]


def test_draw_next_card_raises_on_empty_deck():
    deck = Deck(cards=[])

    with pytest.raises(ValueError, match="Deck is empty."):
        deck.draw_next_card()
