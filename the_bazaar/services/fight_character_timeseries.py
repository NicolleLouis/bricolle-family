import pandas as pd
import plotly.express as px

from the_bazaar.constants.character import Character
from the_bazaar.models import Fight


class FightCharacterTimeseriesService:
    """Generate a line chart of fights per opponent character per day."""

    @classmethod
    def generate(cls):
        fights = Fight.objects.all()
        records = [
            {
                'day': fight.day_number,
                'character': fight.opponent_character,
            }
            for fight in fights
        ]

        if not records:
            df = pd.DataFrame({'day': [], 'character': [], 'count': []})
        else:
            df = pd.DataFrame(records)
            day_range = range(df['day'].min(), df['day'].max() + 1)
            idx = pd.MultiIndex.from_product([day_range, Character.values], names=['day', 'character'])
            df = (
                df.groupby(['day', 'character'])
                  .size()
                  .reindex(idx, fill_value=0)
                  .reset_index(name='count')
            )
        fig = px.line(df, x='day', y='count', color='character')
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
