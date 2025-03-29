from django.contrib import admin

from shopping_list.models import Course, CourseElement, Ingredient, PlannedCourse, ShoppingListItem
from shopping_list.models.course import CourseAdmin
from shopping_list.models.course_element import CourseElementAdmin
from shopping_list.models.ingredient import IngredientAdmin
from shopping_list.models.planned_course import PlannedCourseAdmin
from shopping_list.models.shopping_list_item import ShoppingListItemAdmin

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseElement, CourseElementAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(PlannedCourse, PlannedCourseAdmin)
admin.site.register(ShoppingListItem, ShoppingListItemAdmin)
