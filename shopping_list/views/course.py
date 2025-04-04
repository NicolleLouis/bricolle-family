from django.shortcuts import render, redirect

from shopping_list.forms.course import CourseForm


def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shopping_list:shopping_list')
        else:
            return render(
                request,
                "shopping_list/error.html",
                {"message": "Course already present in database"}
            )
    else:
        form = CourseForm()
    return render(request, 'shopping_list/add_course.html', {'form': form})
