from django.urls import path

from the_bazaar.views.character_aggregate import BazaarAggregate
from the_bazaar.views.monster_beater import MonsterBeaterView
from the_bazaar.views.run_list import RunCreateView, RunUpdateView, RunDeleteView, RunListView

app_name = 'the_bazaar'

urlpatterns = [
    path('', RunListView.as_view(), name='run_list'),
    path('<int:pk>/delete/', RunDeleteView.as_view(), name='run_delete'),
    path('<int:pk>/edit/', RunUpdateView.as_view(), name='run_update'),
    path('add/', RunCreateView.as_view(), name='run_create'),
    path('character_stats/', BazaarAggregate.by_character, name='character_stats'),
    path('monster_beater/<str:monster_name>/', MonsterBeaterView.form, name='monster_beater'),
]
