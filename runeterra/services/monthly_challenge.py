import random

from django.db.models import Count, F

from runeterra.models import Champion


class MonthlyChallengeResetService:
    def __init__(self, queryset=None):
        self._queryset = queryset or Champion.objects.all()

    def reset(self) -> int:
        return self._reset_all()

    def _reset_all(self) -> int:
        return self._queryset.update(monthly_try_remaining=3)


class MonthlyChallengeAvailableService:
    def __init__(self, queryset=None):
        self._queryset = queryset or Champion.objects.all()

    def list_available(self, star_level: int | None = None) -> tuple:
        available = self._available_queryset()
        counts = self._counts_by_star(available)
        total = sum(counts.values())
        if star_level in counts:
            available = available.filter(star_level=star_level)
        return available.order_by("name"), counts, total

    def pick_spotlight(self):
        return self._random_available()

    def _available_queryset(self):
        return self._queryset.filter(monthly_try_remaining__gt=0, star_level__gte=2)

    def _counts_by_star(self, queryset):
        counts = {star: 0 for star in range(2, 8)}
        for row in queryset.values("star_level").annotate(total=Count("id")):
            star_level = row["star_level"]
            if star_level in counts:
                counts[star_level] = row["total"]
        return counts

    def _random_available(self):
        ids = list(self._available_queryset().values_list("id", flat=True))
        if not ids:
            return None
        return self._queryset.filter(id=random.choice(ids)).first()


class MonthlyChallengeConsumeService:
    def __init__(self, queryset=None):
        self._queryset = queryset or Champion.objects.all()

    def consume(self, champion_id: int) -> bool:
        return self._decrement_try(champion_id)

    def _decrement_try(self, champion_id: int) -> bool:
        updated = (
            self._queryset.filter(
                id=champion_id,
                monthly_try_remaining__gt=0,
            )
            .update(monthly_try_remaining=F("monthly_try_remaining") - 1)
        )
        return updated > 0
