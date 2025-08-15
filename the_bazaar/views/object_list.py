import django_filters
from django.urls import reverse_lazy, reverse
from django_filters.views import FilterView
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404, redirect

from the_bazaar.forms.object import ObjectForm
from the_bazaar.models import Object
from the_bazaar.constants.result import Result


class ObjectFilter(django_filters.FilterSet):
    best_win = django_filters.ChoiceFilter(
        choices=[
            (Result.GOLD_WIN, 'Gold'),
            (Result.SILVER_WIN, 'Silver'),
            (Result.BRONZE_WIN, 'Bronze'),
        ],
        empty_label='Any',
    )

    class Meta:
        model = Object
        fields = ['character', 'best_win']


class ObjectListView(FilterView):
    model = Object
    template_name = 'the_bazaar/object_list.html'
    context_object_name = 'objects'
    filterset_class = ObjectFilter
    ordering = ['name']


class ObjectCreateView(CreateView):
    model = Object
    form_class = ObjectForm
    template_name = 'the_bazaar/object_form.html'
    success_url = reverse_lazy('the_bazaar:object_list')


def add_victory(request, pk):
    obj = get_object_or_404(Object, pk=pk)
    if request.method == 'POST':
        victory_type = request.POST.get('victory_type')
        if victory_type == Result.BRONZE_WIN:
            obj.bronze_win_number += 1
        elif victory_type == Result.SILVER_WIN:
            obj.silver_win_number += 1
        elif victory_type == Result.GOLD_WIN:
            obj.gold_win_number += 1
        if obj.gold_win_number > 0:
            obj.best_win = Result.GOLD_WIN
        elif obj.silver_win_number > 0:
            obj.best_win = Result.SILVER_WIN
        elif obj.bronze_win_number > 0:
            obj.best_win = Result.BRONZE_WIN
        else:
            obj.best_win = None
        obj.save()
    return redirect(request.META.get('HTTP_REFERER', reverse('the_bazaar:object_list')))
