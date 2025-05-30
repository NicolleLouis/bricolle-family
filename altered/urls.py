from django.urls import path

from altered.views.home import home

app_name = "altered"

urlpatterns = [
    path("", home, name="home"),
]
