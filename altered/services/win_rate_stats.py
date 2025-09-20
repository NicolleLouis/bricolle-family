from __future__ import annotations

from typing import Optional

from django.db.models import Count, Q, QuerySet

from altered.constants.win_rate_scope import WinRateScope
from altered.models import Champion, Deck, Game
from altered.value_objects import ChampionWinRate


class WinRateStatsService:
    def __init__(
        self,
        scope: str = WinRateScope.ALL,
        faction: Optional[str] = None,
        champion: Optional[Champion] = None,
        deck: Optional[Deck] = None,
    ):
        self.scope = scope or WinRateScope.ALL
        self.faction = faction
        self.champion = champion
        self.deck = deck
        self.games: QuerySet[Game] = self.get_games()
        self.result: list[ChampionWinRate] = []
        self.compute()

    def get_games(self) -> QuerySet[Game]:
        games = Game.objects.select_related("deck", "deck__champion", "opponent_champion")
        if self.scope == WinRateScope.FACTION and self.faction:
            return games.filter(deck__champion__faction=self.faction)
        if self.scope == WinRateScope.CHAMPION and self.champion:
            return games.filter(deck__champion=self.champion)
        if self.scope == WinRateScope.DECK and self.deck:
            return games.filter(deck=self.deck)
        return games

    def compute(self) -> None:
        stats = (
            self.games.values("opponent_champion")
            .annotate(
                match_number=Count("id"),
                win_number=Count("id", filter=Q(is_win=True)),
            )
        )
        stats_map = {
            entry["opponent_champion"]: entry for entry in stats
        }
        champions = Champion.objects.all().order_by("name")
        for champion in champions:
            data = stats_map.get(
                champion.pk,
                {"match_number": 0, "win_number": 0},
            )
            match_number = data["match_number"]
            win_number = data["win_number"]
            win_ratio = (
                round(win_number / match_number * 100, 2)
                if match_number
                else None
            )
            ratio_color = self.get_ratio_color(win_ratio)
            ratio_text_color = self.get_ratio_text_color(win_ratio)
            achievement_color = self.get_achievement_color(match_number, win_number)
            self.result.append(
                ChampionWinRate(
                    champion=champion,
                    match_number=match_number,
                    win_number=win_number,
                    win_ratio=win_ratio,
                    ratio_color=ratio_color,
                    ratio_text_color=ratio_text_color,
                    achievement_color=achievement_color,
                )
            )

    @staticmethod
    def get_ratio_color(win_ratio: Optional[float]) -> str:
        if win_ratio is None:
            return "#e9ecef"
        ratio = max(0.0, min(win_ratio, 100.0))
        red = (220, 53, 69)
        orange = (253, 126, 20)
        yellow = (255, 193, 7)
        green = (25, 135, 84)
        if ratio <= 50:
            factor = ratio / 50
            color = tuple(
                int(red[idx] + (orange[idx] - red[idx]) * factor)
                for idx in range(3)
            )
        else:
            factor = (ratio - 50) / 50
            color = tuple(
                int(yellow[idx] + (green[idx] - yellow[idx]) * factor)
                for idx in range(3)
            )
        return "#{:02x}{:02x}{:02x}".format(*color)

    @staticmethod
    def get_achievement_color(match_number: int, win_number: int) -> str:
        if match_number == 0:
            return "#adb5bd"
        if win_number > 0:
            return "#198754"
        return "#dc3545"

    @staticmethod
    def get_ratio_text_color(win_ratio: Optional[float]) -> str:
        if win_ratio is None:
            return "#212529"
        if win_ratio <= 20 or win_ratio >= 60:
            return "#ffffff"
        return "#212529"
