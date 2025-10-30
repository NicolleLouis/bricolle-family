from django.urls import path

from capitalism.views.home import HomeView
from capitalism.views.settings import SettingView
from capitalism.views.humans import HumansView
from capitalism.views.objects import ObjectsView
from capitalism.views.human_analytics import HumanAnalyticsView
from capitalism.views.price_analytics import PriceAnalyticsView
from capitalism.views.transactions import TransactionsView

app_name = "capitalism"

urlpatterns = [
    path("", HomeView.home, name="home"),
    path("settings/", SettingView.home, name="settings"),
    path("humans/", HumansView.home, name="humans"),
    path("humans/<int:human_id>/", HumansView.detail, name="human_detail"),
    path("objects/", ObjectsView.home, name="objects"),
    path("human-analytics/", HumanAnalyticsView.home, name="human_analytics"),
    path("price-analytics/", PriceAnalyticsView.home, name="price_analytics"),
    path("transactions/", TransactionsView.home, name="transactions"),
]
