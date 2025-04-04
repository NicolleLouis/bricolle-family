from django.urls import path

from shopping_list.views.cart import cart
from shopping_list.views.configuration import configuration
from shopping_list.views.course import CourseController
from shopping_list.views.home import home
from shopping_list.views.ingredient import add_ingredient
from shopping_list.views.list import shopping_list
from shopping_list.views.login import Login
from shopping_list.views.meal import meal
from shopping_list.views.planned_course import PlannedCourseController
from shopping_list.views.planned_ingredients import PlannedIngredientController

app_name = "shopping_list"

urlpatterns = [
    path("", home, name="home"),
    path("cart/", cart, name="cart"),
    path("configuration", configuration, name="configuration"),
    path("course/new", CourseController.add_course, name="add_course"),
    path("course/<int:course_id>/edit", CourseController.edit_course, name="edit_course"),
    path("ingredient/new", add_ingredient, name="add_ingredient"),
    path("login/", Login.user_login, name="login"),
    path("logout/", Login.user_logout, name="logout"),
    path("meal/", meal, name="meal"),
    path("planned_course/", PlannedCourseController.index, name="planned_course"),
    path("planned_course/add", PlannedCourseController.add_api, name="planned_course_add_api"),
    path("planned_course/delete", PlannedCourseController.delete, name="planned_course_delete"),
    path("planned_course/new", PlannedCourseController.add_page, name="planned_course_add_page"),
    path("register/", Login.register, name="register"),
    path("shopping_list", shopping_list, name="list"),
    path("shopping_list/", PlannedIngredientController.index, name="shopping_list"),
    path("shopping_list/add", PlannedIngredientController.add_api, name="shopping_list_add_api"),
    path("shopping_list/delete", PlannedIngredientController.delete, name="shopping_list_delete"),
    path("shopping_list/new", PlannedIngredientController.add_page, name="shopping_list_add_page"),
]
