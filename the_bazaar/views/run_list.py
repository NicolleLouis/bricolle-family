import django_filters
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, DeleteView
from django_filters.views import FilterView

from the_bazaar.forms.run import RunForm
from the_bazaar.models import Run, Archetype


class RunFilter(django_filters.FilterSet):
    class Meta:
        model = Run
        fields = ['character', 'archetype', 'result']


class RunListView(FilterView):
    model = Run
    template_name = "the_bazaar/run_list.html"
    context_object_name = 'runs'
    filterset_class = RunFilter
    ordering = ['-created_at']

class RunCreateView(CreateView):
    model = Run
    form_class = RunForm
    template_name = 'the_bazaar/run_form.html'
    success_url = reverse_lazy('the_bazaar:run_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['archetype'].queryset = Archetype.objects.filter(is_meta_viable=True)
        return form


class RunUpdateView(UpdateView):
    model = Run
    form_class = RunForm
    template_name = 'the_bazaar/run_form.html'
    success_url = reverse_lazy('the_bazaar:run_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['archetype'].queryset = Archetype.objects.filter(is_meta_viable=True)
        return form


class RunDeleteView(DeleteView):
    model = Run
    template_name = 'the_bazaar/run_form_delete.html'
    success_url = reverse_lazy('the_bazaar:run_list')
