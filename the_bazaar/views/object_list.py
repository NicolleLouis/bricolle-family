import django_filters
from django.urls import reverse_lazy
from django_filters.views import FilterView
from django.views.generic import CreateView

from the_bazaar.forms.object import ObjectForm
from the_bazaar.models import Object


class ObjectFilter(django_filters.FilterSet):
    class Meta:
        model = Object
        fields = ['character', 'was_mastered']


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
