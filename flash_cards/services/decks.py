from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class FlashCard:
    question: str
    answer: str


@dataclass(frozen=True)
class FlashCardDeck:
    title: str
    description: str
    cards: Tuple[FlashCard, ...]


class FlashCardService:
    """Provide read-only flash card decks that can later be persisted."""

    def __init__(self) -> None:
        self._decks: Tuple[FlashCardDeck, ...] = self._build_decks()

    def get_decks(self) -> Tuple[FlashCardDeck, ...]:
        return self._decks

    def _build_decks(self) -> Tuple[FlashCardDeck, ...]:
        configs = (
            {
                "title": "Conjugaison",
                "description": "Révisez les bases du présent en français.",
                "cards": (
                    {"question": "Je ___ (avoir)", "answer": "ai"},
                    {"question": "Nous ___ (être)", "answer": "sommes"},
                    {"question": "Ils ___ (aller)", "answer": "vont"},
                ),
            },
            {
                "title": "Capitals",
                "description": "Capitales européennes importantes.",
                "cards": (
                    {"question": "Capital of France", "answer": "Paris"},
                    {"question": "Capital of Spain", "answer": "Madrid"},
                    {"question": "Capital of Italy", "answer": "Rome"},
                ),
            },
        )

        decks: list[FlashCardDeck] = []
        for deck in configs:
            cards = tuple(FlashCard(**card) for card in deck["cards"])
            decks.append(
                FlashCardDeck(deck["title"], deck["description"], cards)
            )
        return tuple(decks)
