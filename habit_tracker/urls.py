from django.urls import path, include

from habit_tracker.views.bazaar.character_aggregate import BazaarAggregate
from habit_tracker.views.bazaar.rogue_scrapper_beater import RogueScrapperBeaterView
from habit_tracker.views.bazaar.run_list import RunCreateView, RunUpdateView, RunDeleteView, RunListView
from habit_tracker.views.home import home
from habit_tracker.views.login import Login

app_name = 'habit_tracker'

bazaar_urls = [
    path('', RunListView.as_view(), name='bazaar'),
    path('<int:pk>/delete/', RunDeleteView.as_view(), name='bazaar_run_delete'),
    path('<int:pk>/edit/', RunUpdateView.as_view(), name='bazaar_run_update'),
    path('add/', RunCreateView.as_view(), name='bazaar_run_create'),
    path('character_stats/', BazaarAggregate.by_character, name='bazaar_character_stats'),
    path('rogue_scrapper_beater/', RogueScrapperBeaterView.form, name='rogue_scrapper_beater'),
]

urlpatterns = [
    path('', home, name='home'),
    path('bazaar/', include(bazaar_urls)),
    path('login/', Login.user_login, name='login'),
    path('logout/', Login.user_logout, name='logout'),
    path('register/', Login.register, name='register'),
]
