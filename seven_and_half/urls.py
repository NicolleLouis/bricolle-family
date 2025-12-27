from django.urls import path

from seven_and_half.views.draw_probability import draw_probability
from seven_and_half.views.game_simulation import game_simulation
from seven_and_half.views.home import home

app_name = "seven_and_half"

urlpatterns = [
    path("", home, name="home"),
    path("draw-probability/", draw_probability, name="draw_probability"),
    path("game-simulation/", game_simulation, name="game_simulation"),
]
