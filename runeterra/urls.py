from django.urls import path

from runeterra import views

app_name = "runeterra"

urlpatterns = [
    path("", views.random_picker, name="random_picker"),
    path("champions/", views.champion_list, name="champion_list"),
]
