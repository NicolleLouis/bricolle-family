from django.shortcuts import render, redirect, get_object_or_404

from shopping_list.forms.course import CourseForm
from shopping_list.forms.course_element import CourseElementFormSet
from shopping_list.models import Course


class CourseController:
    @staticmethod
    def index(request):
        courses = Course.objects.all()

        return render(request, 'shopping_list/index_course.html', {'courses': courses})

    @staticmethod
    def add_course(request):
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                course = form.save()
                return redirect('shopping_list:edit_course', course_id=course.id)
            else:
                return render(
                    request,
                    "shopping_list/error.html",
                    {"message": "Course already present in database"}
                )
        else:
            form = CourseForm()
        return render(request, 'shopping_list/add_course.html', {'form': form})


    @staticmethod
    def edit_course(request, course_id):
        course = get_object_or_404(Course, id=course_id)
        if request.method == 'POST':
            form = CourseForm(request.POST, instance=course)
            formset = CourseElementFormSet(request.POST, instance=course)
            if form.is_valid() and formset.is_valid():
                form.save()
                formset.save()
                return redirect('shopping_list:configuration')
            else:
                return render(
                    request,
                    "shopping_list/error.html",
                    {"message": "There was an issue while saving this course"}
                )
        else:
            form = CourseForm(instance=course)
            formset = CourseElementFormSet(instance=course)

        return render(request, 'shopping_list/edit_course.html', {
            'form': form,
            'formset': formset,
            'course': course,
        })
