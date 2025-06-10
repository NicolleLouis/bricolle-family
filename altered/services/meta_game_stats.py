from datetime import timedelta
from django.db.models import Count, Q
from django.utils import timezone

from altered.constants.duration import Duration
from altered.models import Champion, Game
from altered.value_objects.champion_game_stats import ChampionGameStats


class MetaGameStatsService:
    def __init__(self, duration: str = Duration.ALL):
        self.duration = duration or Duration.ALL
        self.games = self.get_games()
        self.result: list[ChampionGameStats] = []
        self.compute()

    def get_games(self):
        qs = Game.objects.all()
        if self.duration == Duration.LAST_MONTH:
            qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=30))
        elif self.duration == Duration.LAST_3_MONTHS:
            qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=90))
        elif self.duration == Duration.LAST_6_MONTHS:
            qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=180))
        return qs

    def compute(self):
        data = (
            self.games.values('opponent_champion')
            .annotate(
                match_number=Count('id'),
                win_number=Count('id', filter=Q(is_win=True))
            )
            .order_by('-match_number')
        )
        for entry in data:
            champion = Champion.objects.get(pk=entry['opponent_champion'])
            match_number = entry['match_number']
            win_number = entry['win_number']
            win_ratio = round(win_number / match_number * 100, 2) if match_number else 0.0
            self.result.append(
                ChampionGameStats(
                    champion=champion,
                    match_number=match_number,
                    win_number=win_number,
                    win_ratio=win_ratio,
                )
            )

