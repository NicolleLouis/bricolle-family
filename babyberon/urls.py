from django.urls import path

from babyberon.views.home import home
from babyberon.views.login import Login
from babyberon.views.baby_bottle import BabyBottleController

app_name = "babyberon"

urlpatterns = [
    path("", home, name="home"),
    path('login/', Login.user_login, name='login'),
    path('logout/', Login.user_logout, name='logout'),
    path('baby-bottle/add/', BabyBottleController.add_baby_bottle, name='add_baby_bottle'),
]
