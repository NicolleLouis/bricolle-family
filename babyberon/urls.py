from django.urls import path

from babyberon.views.home import home
from babyberon.views.baby_bottle import BabyBottleController

app_name = "babyberon"

urlpatterns = [
    path("", home, name="home"),
    path('baby-bottle/add/', BabyBottleController.add_baby_bottle, name='add_baby_bottle'),
]
