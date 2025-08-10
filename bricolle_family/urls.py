from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from bricolle_family import settings
from bricolle_family.views.login import Login
from bricolle_family.views.summary import SummaryView

urlpatterns = [
    path("", SummaryView.home, name="home"),
    path("games", SummaryView.games, name="games"),
    path("more", SummaryView.more, name="more"),


    path("admin/", admin.site.urls),
    path("altered/", include("altered.urls")),
    path("baby_name/", include("baby_name.urls")),
    path("babyberon/", include("babyberon.urls")),
    path("battery_simulator/", include("battery_simulator.urls")),
    path("runeterra/", include("runeterra.urls")),
    path("login", Login.user_login, name="login"),
    path("logout", Login.user_logout, name="logout"),
    path("northguard/", include("northguard.urls")),
    path("chess/", include("chess.urls")),
    path("games_collection/", include("games_collection.urls")),
    path("docs/", include("documents.urls")),
    path("shopping_list/", include("shopping_list.urls")),
    path("the_bazaar/", include("the_bazaar.urls")),
]

if settings.ENV == 'local':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
