from django.urls import path

from runeterra import views

app_name = "runeterra"

urlpatterns = [
    path("", views.random_picker, name="random_picker"),
    path("champions/", views.champion_list, name="champion_list"),
    path("champions/new/", views.ChampionCreateView.as_view(), name="champion_create"),
    path("champions/<int:pk>/edit/", views.ChampionUpdateView.as_view(), name="champion_update"),
]
