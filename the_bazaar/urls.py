from django.urls import path

from the_bazaar.views.character_aggregate import BazaarAggregate
from the_bazaar.views.archetype_aggregate import BazaarAggregate as ArchetypeBazaarAggregate
from the_bazaar.views.monster_beater import MonsterBeaterView
from the_bazaar.views.run_list import RunCreateView, RunUpdateView, RunDeleteView, RunListView
from the_bazaar.views.object_list import ObjectListView, ObjectCreateView, add_victory
from the_bazaar.views.object_stats import ObjectStatsView
from the_bazaar.views.greenheart_dungeon import GreenheartDungeonView
from the_bazaar.views.meta import MetaView

app_name = 'the_bazaar'

urlpatterns = [
    path('', RunListView.as_view(), name='run_list'),
    path('<int:pk>/delete/', RunDeleteView.as_view(), name='run_delete'),
    path('<int:pk>/edit/', RunUpdateView.as_view(), name='run_update'),
    path('add/', RunCreateView.as_view(), name='run_create'),
    path('character_stats/', BazaarAggregate.by_character, name='character_stats'),
    path('archetype_stats/', ArchetypeBazaarAggregate.by_archetype, name='archetype_stats'),
    path('monster_beater/<str:monster_name>/', MonsterBeaterView.form, name='monster_beater'),
    path('monster_beater_home', MonsterBeaterView.home, name='monster_beater_home'),
    path('object/', ObjectListView.as_view(), name='object_list'),
    path('object/new/', ObjectCreateView.as_view(), name='object_create'),
    path('object/<int:pk>/add_victory/', add_victory, name='object_add_victory'),
    path('object_stats/', ObjectStatsView.stats, name='object_stats'),
    path('greenheart_dungeon/', GreenheartDungeonView.stats, name='greenheart_dungeon'),
    path('meta/', MetaView.stats, name='meta'),
]

