from django.core.exceptions import ValidationError
import plotly.express as px
from collections import Counter

from core.services.charts.figure_to_image import FigureToImage
from the_bazaar.models import Run, Season


class CharacterRunRepartitionService:
    @classmethod
    def generate(cls, run_range=None):
        runs = cls.get_runs(run_range)
        fig = cls.generate_figure(runs)
        return FigureToImage.generate_chart_image(fig)

    @staticmethod
    def get_runs(run_range=None):
        if run_range is None or run_range == 'current_season':
            newest_season = Season.objects.order_by('-created_at').first()
            return Run.objects.filter(
                season=newest_season
            )
        elif run_range == 'all_time':
            return Run.objects.all()
        else:
            raise ValidationError(f'run_range {run_range} not implemented')

    @classmethod
    def generate_figure(cls, runs):
        character_counts = Counter(run.character for run in runs)

        data = {
            'Character': list(character_counts.keys()),
            'Count': list(character_counts.values())
        }

        fig = px.pie(
            data,
            names='Character',
            values='Count',
        )

        return fig
