from django.urls import path

from flash_cards.views.home import home
from flash_cards.views.settings import (
    categories,
    question_delete,
    question_form,
    settings,
)

app_name = "flash_cards"

urlpatterns = [
    path("", home, name="home"),
    path("settings/", settings, name="settings"),
    path("categories/", categories, name="categories"),
    path("questions/add/", question_form, name="question_create"),
    path("questions/<int:question_id>/edit/", question_form, name="question_edit"),
    path("questions/<int:question_id>/delete/", question_delete, name="question_delete"),
]
