from django.urls import path

from flash_cards.views.api import (
    create_question,
    list_categories,
    needs_rework_question,
    update_question,
)
from flash_cards.views.hall_of_fame import hall_of_fame
from flash_cards.views.home import home
from flash_cards.views.settings import (
    category_delete,
    categories,
    question_delete,
    question_form,
    question_json_form,
    settings,
)
from flash_cards.views.theme_presets import theme_presets
from flash_cards.views.statistics import statistics

app_name = "flash_cards"

urlpatterns = [
    path("", home, name="home"),
    path("statistics/", statistics, name="statistics"),
    path("hall-of-fame/", hall_of_fame, name="hall_of_fame"),
    path("settings/", settings, name="settings"),
    path("categories/", categories, name="categories"),
    path("categories/<int:category_id>/delete/", category_delete, name="category_delete"),
    path("theme-presets/", theme_presets, name="theme_presets"),
    path("theme-presets/<int:preset_id>/", theme_presets, name="theme_preset_edit"),
    path("questions/add/", question_form, name="question_create"),
    path("questions/add/json/", question_json_form, name="question_create_json"),
    path("questions/<int:question_id>/edit/", question_form, name="question_edit"),
    path("questions/<int:question_id>/delete/", question_delete, name="question_delete"),
    path("api/questions/", create_question, name="api_question_create"),
    path(
        "api/questions/needs-rework/",
        needs_rework_question,
        name="api_question_needs_rework",
    ),
    path("api/questions/<int:question_id>/", update_question, name="api_question_update"),
    path("api/categories/", list_categories, name="api_categories"),
]
