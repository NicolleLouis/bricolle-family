from django.shortcuts import render, get_object_or_404, redirect

from shopping_list.forms.course_history import CourseHistoryForm

from shopping_list.models import CourseHistory


class CourseHistoryController:
    @staticmethod
    def index(request):
        courses = CourseHistory.objects.all()

        min_score = request.GET.get('min_score')
        if min_score and min_score.isdigit():
            courses = courses.filter(rating__gte=int(min_score))

        max_score = request.GET.get('max_score')
        if max_score and max_score.isdigit():
            courses = courses.filter(rating__lte=int(max_score))

        courses = courses.order_by('-created_at')[:10]

        return render(
            request,
            'shopping_list/index_course_history.html',
            {
                'courses': courses,
                'min_score': min_score,
                'max_score': max_score,
            }
        )

    @staticmethod
    def edit(request, history_id):
        history = get_object_or_404(CourseHistory, id=history_id)

        if request.method == 'POST':
            form = CourseHistoryForm(request.POST, instance=history)
            if form.is_valid():
                form.save()
                return redirect('shopping_list:course_history')
        else:
            form = CourseHistoryForm(instance=history)

        return render(
            request,
            'shopping_list/edit_course_history.html',
            {
                'form': form,
                'history': history,
            }
        )
