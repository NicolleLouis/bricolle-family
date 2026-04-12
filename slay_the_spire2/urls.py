from django.urls import path

from slay_the_spire2.views.boss import boss
from slay_the_spire2.views.card import card
from slay_the_spire2.views.character import character
from slay_the_spire2.views.death_type import death_type
from slay_the_spire2.views.documents import DocumentController
from slay_the_spire2.views.elite import elite
from slay_the_spire2.views.home import home
from slay_the_spire2.views.relic import relic
from slay_the_spire2.views.settings import settings
from slay_the_spire2.views.upload import upload

app_name = "slay_the_spire2"

urlpatterns = [
    path("", home, name="home"),
    path("boss/", boss, name="boss"),
    path("card/", card, name="card"),
    path("character/", character, name="character"),
    path("death-type/", death_type, name="death_type"),
    path("elite/", elite, name="elite"),
    path("ideas/", DocumentController.ideas, name="ideas"),
    path("relic/", relic, name="relic"),
    path("upload/", upload, name="upload"),
    path("settings/", settings, name="settings"),
]
