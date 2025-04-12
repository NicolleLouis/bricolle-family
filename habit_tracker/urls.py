from django.urls import path

from habit_tracker.views.bazaar_aggregate import BazaarAggregate
from habit_tracker.views.bazaar_list import BazaarRunListView, BazaarRunCreateView, BazaarRunUpdateView, BazaarRunDeleteView
from habit_tracker.views.home import home
from habit_tracker.views.login import Login

app_name = 'habit_tracker'

urlpatterns = [
    path('', home, name='home'),
    path('bazaar', BazaarRunListView.as_view(), name='bazaar'),
    path('bazaar/<int:pk>/delete/', BazaarRunDeleteView.as_view(), name='bazaar_run_delete'),
    path('bazaar/<int:pk>/edit/', BazaarRunUpdateView.as_view(), name='bazaar_run_update'),
    path('bazaar/add/', BazaarRunCreateView.as_view(), name='bazaar_run_create'),
    path('bazaar/character_stats/', BazaarAggregate.by_character, name='bazaar_character_stats'),
    path('login/', Login.user_login, name='login'),
    path('logout/', Login.user_logout, name='logout'),
    path('register/', Login.register, name='register'),
]
