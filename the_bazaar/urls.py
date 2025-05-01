from django.urls import path

from the_bazaar.views.character_aggregate import BazaarAggregate
from the_bazaar.views.rogue_scrapper_beater import RogueScrapperBeaterView
from the_bazaar.views.run_list import RunCreateView, RunUpdateView, RunDeleteView, RunListView
from the_bazaar.views.login import Login

app_name = 'the_bazaar'

urlpatterns = [
    path('', RunListView.as_view(), name='run_list'),
    path('<int:pk>/delete/', RunDeleteView.as_view(), name='run_delete'),
    path('<int:pk>/edit/', RunUpdateView.as_view(), name='run_update'),
    path('add/', RunCreateView.as_view(), name='run_create'),
    path('character_stats/', BazaarAggregate.by_character, name='character_stats'),
    path('login/', Login.user_login, name='login'),
    path('logout/', Login.user_logout, name='logout'),
    path('rogue_scrapper_beater/', RogueScrapperBeaterView.form, name='rogue_scrapper_beater'),
]
