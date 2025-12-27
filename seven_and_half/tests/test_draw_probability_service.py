from seven_and_half.services.deck_service import Card, Deck, DeckService
from seven_and_half.services.draw_probability_service import DrawProbabilityService


class _StubDeckService(DeckService):
    def __init__(self, deck: Deck) -> None:
        self._deck = deck

    def create_shuffled_deck(self) -> Deck:
        return self._deck


def test_calculate_draw_probabilities_counts_busts():
    deck = Deck(cards=[Card(value=2), Card(value=1), Card(value=7), Card(value="Joker")])
    service = DrawProbabilityService(deck_service=_StubDeckService(deck))

    result = service.calculate_draw_probabilities(initial_card_value=2)

    assert result.total_cards == 3
    assert result.bust_cards == 1
    assert result.bust_probability == 1 / 3
    assert result.success_probability == 2 / 3
