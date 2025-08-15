from django.db.models import Avg
from django.shortcuts import render

from the_bazaar.models import Run


class GreenheartDungeonView:
    @staticmethod
    def stats(request):
        runs_post_dungeon_patch = Run.objects.filter(season__number__gte=3)
        total_runs = runs_post_dungeon_patch.count()
        runs_with = runs_post_dungeon_patch.filter(greenheart_dungeon=True)
        runs_without = runs_post_dungeon_patch.filter(greenheart_dungeon=False)

        if total_runs:
            ratio = runs_with.count() / total_runs * 100
        else:
            ratio = 0

        avg_with = runs_with.aggregate(avg=Avg('win_number'))['avg'] or 0
        avg_without = runs_without.aggregate(avg=Avg('win_number'))['avg'] or 0

        return render(
            request,
            'the_bazaar/greenheart_dungeon.html',
            {
                'ratio': ratio,
                'avg_with': avg_with,
                'avg_without': avg_without,
            }
        )

