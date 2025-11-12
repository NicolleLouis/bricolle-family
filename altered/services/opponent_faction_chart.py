from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable

import plotly.express as px

from altered.constants.faction import Faction
from altered.constants.faction_colors import FACTION_COLORS
from altered.value_objects.champion_game_stats import ChampionGameStats


class OpponentFactionChartService:
    """Render a pie chart describing how opponent factions are represented."""

    def __init__(self, stats: Iterable[ChampionGameStats]):
        self._stats = list(stats)
        self._label_lookup = dict(Faction.choices)

    def render(self) -> str:
        counts = self._faction_counts()
        if not counts:
            return ""

        labels = list(counts.keys())
        values = [counts[label] for label in labels]
        color_map = self._color_map()

        fig = px.pie(
            names=labels,
            values=values,
            title="Opponent Faction Representation",
            color=labels,
            color_discrete_map=color_map,
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))

        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def _faction_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for stat in self._stats:
            matches = stat.match_number or 0
            if matches <= 0:
                continue
            label = self._label_lookup.get(stat.champion.faction, stat.champion.faction)
            counts[label] += matches

        return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))

    def _color_map(self) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        for faction_value, color in FACTION_COLORS.items():
            label = self._label_lookup.get(faction_value, faction_value)
            mapping[label] = color
        return mapping
