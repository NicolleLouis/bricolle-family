from django.db.models import Avg
from django.shortcuts import render

from the_bazaar.models import Run, Dungeon


class DungeonView:
    @staticmethod
    def stats(request):
        dungeon_stats = []
        dungeons = Dungeon.objects.order_by('season_apparition', 'name')
        for dungeon in dungeons:
            if dungeon.season_apparition is None:
                runs_post_dungeon_patch = Run.objects.none()
            else:
                runs_post_dungeon_patch = Run.objects.filter(
                    season__number__gte=dungeon.season_apparition
                )
            total_runs = runs_post_dungeon_patch.count()
            runs_with = runs_post_dungeon_patch.filter(dungeons=dungeon)
            runs_without = runs_post_dungeon_patch.exclude(dungeons=dungeon)

            if total_runs:
                ratio = runs_with.count() / total_runs * 100
            else:
                ratio = 0

            avg_with = runs_with.aggregate(avg=Avg('win_number'))['avg'] or 0
            avg_without = runs_without.aggregate(avg=Avg('win_number'))['avg'] or 0

            dungeon_stats.append(
                {
                    'dungeon': dungeon,
                    'ratio': ratio,
                    'avg_with': avg_with,
                    'avg_without': avg_without,
                    'total_runs': total_runs,
                }
            )

        multi_dungeon_stats = {}
        runs_with_multiple_dungeons = (
            Run.objects.prefetch_related('dungeons')
            .filter(dungeons__isnull=False)
            .distinct()
        )
        for run in runs_with_multiple_dungeons:
            dungeon_names = sorted(run.dungeons.values_list('name', flat=True))
            if len(dungeon_names) < 2:
                continue
            key = tuple(dungeon_names)
            if key not in multi_dungeon_stats:
                multi_dungeon_stats[key] = {
                    'combination': " + ".join(dungeon_names),
                    'run_count': 0,
                    'win_total': 0,
                }
            multi_dungeon_stats[key]['run_count'] += 1
            multi_dungeon_stats[key]['win_total'] += run.win_number

        multi_dungeon_stats_list = []
        for entry in multi_dungeon_stats.values():
            if entry['run_count']:
                avg_win_number = entry['win_total'] / entry['run_count']
            else:
                avg_win_number = 0
            multi_dungeon_stats_list.append(
                {
                    'combination': entry['combination'],
                    'run_count': entry['run_count'],
                    'avg_win_number': avg_win_number,
                }
            )
        multi_dungeon_stats_list.sort(key=lambda item: (-item['run_count'], item['combination']))

        return render(
            request,
            'the_bazaar/dungeon.html',
            {
                'dungeon_stats': dungeon_stats,
                'multi_dungeon_stats': multi_dungeon_stats_list,
            }
        )
