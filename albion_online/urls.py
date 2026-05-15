from django.urls import path

from albion_online.views.craft_profitability import craft_profitability_mark_done
from albion_online.views.artifact_salvage import artifact_salvage, artifact_salvage_refresh_targets
from albion_online.views.home import home
from albion_online.views.gathering_gear import (
    gathering_gear,
    gathering_gear_detail_panel,
    gathering_gear_profitability,
)
from albion_online.views.leather_jacket import (
    leather_jacket,
    leather_jacket_detail_panel,
    leather_jacket_profitability,
)
from albion_online.views.price_refresh_job import price_refresh_job_status
from albion_online.views.settings_page import settings_page

app_name = "albion_online"

urlpatterns = [
    path("", home, name="home"),
    path("artifact_salvage/", artifact_salvage, name="artifact_salvage"),
    path(
        "artifact_salvage/debug/refresh-targets/",
        artifact_salvage_refresh_targets,
        name="artifact_salvage_refresh_targets",
    ),
    path("gathering_gear/", gathering_gear, name="gathering_gear"),
    path("gathering_gear/detail/", gathering_gear_detail_panel, name="gathering_gear_detail_panel"),
    path("craft_profitability/done/", craft_profitability_mark_done, name="craft_profitability_mark_done"),
    path("gathering_gear/profitable/done/", craft_profitability_mark_done, name="gathering_gear_mark_done"),
    path("gathering_gear/profitable/", gathering_gear_profitability, name="gathering_gear_profitability"),
    path("leather_jacket/", leather_jacket, name="leather_jacket"),
    path("leather_jacket/detail/", leather_jacket_detail_panel, name="leather_jacket_detail_panel"),
    path("leather_jacket/profitable/", leather_jacket_profitability, name="leather_jacket_profitability"),
    path("price_refresh_jobs/<int:job_id>/status/", price_refresh_job_status, name="price_refresh_job_status"),
    path("settings/", settings_page, name="settings"),
]
