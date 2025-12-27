from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.templatetags.static import static as static_url

from bricolle_family import settings
from bricolle_family.views.login import Login
from bricolle_family.views.summary import SummaryView

urlpatterns = [
    path("", SummaryView.home, name="home"),
    path("games", SummaryView.games, name="games"),
    path("more", SummaryView.more, name="more"),
    path("favicon.ico", RedirectView.as_view(url=static_url("favicon.svg"), permanent=True)),


    path("admin/", admin.site.urls),
    path("altered/", include("altered.urls")),
    path("baby_name/", include("baby_name.urls")),
    path("agathe/", include("agathe.urls")),
    path("finance_simulator/", include("finance_simulator.urls")),
    path("runeterra/", include("runeterra.urls")),
    path("civilization7/", include("civilization7.urls")),
    path("flash_cards/", include("flash_cards.urls")),
    path("login", Login.user_login, name="login"),
    path("logout", Login.user_logout, name="logout"),
    path("games_collection/", include("games_collection.urls")),
    path("documents/", include("documents.urls")),
    path("the_bazaar/", include("the_bazaar.urls")),
    path("capitalism/", include("capitalism.urls")),
    path("chess/", include("chess.urls")),
    path("seven_and_half/", include("seven_and_half.urls")),
]

if settings.ENV == 'local':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
