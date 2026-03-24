from django.urls import path

from corwave.views.home import home

app_name = "corwave"

urlpatterns = [
    path("", home, name="home"),
]
