from django.urls import path

from babyberon.views.home import home
from babyberon.views.baby_bottle import BabyBottleController
from babyberon.views.contraction import ContractionController

app_name = "babyberon"

urlpatterns = [
    path("", home, name="home"),
    path("baby-bottle/add/", BabyBottleController.add_baby_bottle, name="add_baby_bottle"),
    path("contractions/", ContractionController.page, name="contractions"),
    path("api/contraction/<int:power>/", ContractionController.add, name="api_add_contraction"),
]
