from django.shortcuts import render

from shopping_list.models import CourseHistory


class CourseHistoryController:
    @staticmethod
    def index(request):
        courses = CourseHistory.objects.all().order_by('-created_at')[:10]

        return render(request, 'shopping_list/index_course_history.html', {'courses': courses})
