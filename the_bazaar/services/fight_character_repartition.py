from collections import Counter

import plotly.express as px

from the_bazaar.models import Fight


class FightCharacterRepartitionService:
    """Generate a pie chart of fights per opponent character."""

    @classmethod
    def generate(cls):
        fights = Fight.objects.all()
        counts = Counter(fight.opponent_character for fight in fights)
        data = {
            'Character': list(counts.keys()),
            'Count': list(counts.values()),
        }
        fig = px.pie(data, names='Character', values='Count')
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
