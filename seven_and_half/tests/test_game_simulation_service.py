from seven_and_half.services.deck_service import Card, Deck, DeckService
from seven_and_half.services.game_simulation_service import GameSimulationService


def _stubbed_create_shuffled_deck(cards_template):
    def _create_shuffled_deck() -> Deck:
        return Deck(cards=[Card(value=card.value) for card in cards_template])

    return _create_shuffled_deck


def test_simulation_counts_player_wins(monkeypatch):
    cards_template = [
        Card(value=2),
        Card(value=5),
        Card(value=6),
    ]
    monkeypatch.setattr(
        DeckService,
        "create_shuffled_deck",
        _stubbed_create_shuffled_deck(cards_template),
    )
    service = GameSimulationService()

    result = service.simulate_games(player_card_value=2, bank_card_value=5, simulations=1)

    assert result.player_wins == 0
    assert result.bank_wins == 1


def test_simulation_counts_player_win_when_bank_busts(monkeypatch):
    cards_template = [
        Card(value=6),
        Card(value=4),
        Card(value=7),
    ]
    monkeypatch.setattr(
        DeckService,
        "create_shuffled_deck",
        _stubbed_create_shuffled_deck(cards_template),
    )
    service = GameSimulationService()

    result = service.simulate_games(player_card_value=6, bank_card_value=4, simulations=1)

    assert result.player_wins == 1
    assert result.bank_wins == 0


def test_simulation_supports_random_player_card(monkeypatch):
    cards_template = [
        Card(value=2),
        Card(value=5),
        Card(value=7),
    ]
    monkeypatch.setattr(
        DeckService,
        "create_shuffled_deck",
        _stubbed_create_shuffled_deck(cards_template),
    )
    service = GameSimulationService()

    result = service.simulate_games(player_card_value=None, bank_card_value=5, simulations=1)

    assert result.simulations == 1


def test_simulation_supports_random_bank_card(monkeypatch):
    cards_template = [
        Card(value=5),
        Card(value=2),
        Card(value=7),
    ]
    monkeypatch.setattr(
        DeckService,
        "create_shuffled_deck",
        _stubbed_create_shuffled_deck(cards_template),
    )
    service = GameSimulationService()

    result = service.simulate_games(player_card_value=5, bank_card_value=None, simulations=1)

    assert result.simulations == 1
