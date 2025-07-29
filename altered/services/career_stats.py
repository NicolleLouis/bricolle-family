from altered.models import Champion, Game
from altered.value_objects.career_champion_stats import CareerChampionStats


class CareerStatsService:
    def __init__(self, faction: str | None = None, name: str | None = None, missing_only: bool = False):
        self.faction = faction
        self.name = name
        self.missing_only = missing_only
        self.result: list[CareerChampionStats] = []
        self.compute()

    def compute(self):
        champions = Champion.objects.all()
        if self.faction:
            champions = champions.filter(faction=self.faction)
        if self.name:
            champions = champions.filter(name__icontains=self.name)
        champions = champions.order_by('name')
        for champion in champions:
            win_number = Game.objects.filter(deck__champion=champion, is_win=True).count()
            if self.missing_only and win_number > 0:
                continue
            self.result.append(CareerChampionStats(champion=champion, win_number=win_number))
