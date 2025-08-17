from django.urls import path

from runeterra import views

app_name = "runeterra"

urlpatterns = [
    path("", views.random_picker, name="random_picker"),
    path("objectives/", views.objectives, name="objectives"),
    path("ideas/", views.ideas, name="ideas"),
    path("stats/", views.region_stats, name="region_stats"),
    path("champions/", views.champion_list, name="champion_list"),
    path("champions/new/", views.ChampionCreateView.as_view(), name="champion_create"),
    path("champions/<int:pk>/edit/", views.ChampionUpdateView.as_view(), name="champion_update"),
]
