import json

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from shopping_list.models import Course, PlannedCourse


class PlannedCourseController:
    @staticmethod
    def index(request):
        planned_courses = PlannedCourse.objects.all()

        return render(
            request,
            "shopping_list/planned_course.html",
            {"planned_courses": planned_courses}
        )

    @staticmethod
    def delete(request):
        try:
            data = json.loads(request.body)
            planned_course_id = data.get('planned_course_id')
            if not planned_course_id:
                return JsonResponse({"status": "error", "message": "Missing planned_course_id."}, status=400)

            planned_course = get_object_or_404(PlannedCourse, id=planned_course_id)
            planned_course.delete()

            return JsonResponse({"status": "success", "message": "Course removed."})

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")

    @staticmethod
    def add_api(request):
        course_id = request.POST.get("course_id")
        if not course_id:
            return JsonResponse({"status": "error", "message": "Missing course_id."}, status=400)

        course = get_object_or_404(Course, id=course_id)

        planned_course, created = PlannedCourse.objects.get_or_create(course=course, defaults={'quantity': 1})
        if not created:
            planned_course.quantity += 1
            planned_course.save()

        return redirect('shopping_list:planned_courses')

    @staticmethod
    def add_page(request):
        courses = Course.objects.all()

        return render(
            request,
            "shopping_list/add_planned_course.html",
            {"courses": courses}
        )
