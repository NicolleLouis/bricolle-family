from django.urls import path

from runeterra import views

app_name = "runeterra"

urlpatterns = [
    path("", views.random_picker, name="random_picker"),
]
