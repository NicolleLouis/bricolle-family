from flash_cards.services.decks import FlashCardService


def test_get_decks_returns_read_only_structures():
    service = FlashCardService()

    decks = service.get_decks()

    assert len(decks) == 2
    first_deck = decks[0]
    assert first_deck.title == "Conjugaison"
    assert first_deck.cards[0].question == "Je ___ (avoir)"
    assert first_deck.cards[0].answer == "ai"
