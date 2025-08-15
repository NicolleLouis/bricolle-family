from django.db.models import Avg
from django.shortcuts import render

from the_bazaar.models import Run


class GreenheartDungeonView:
    @staticmethod
    def stats(request):
        total_runs = Run.objects.count()
        runs_with = Run.objects.filter(greenheart_dungeon=True)
        runs_without = Run.objects.filter(greenheart_dungeon=False)

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

