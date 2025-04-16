import django_filters
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, DeleteView
from django_filters.views import FilterView

from habit_tracker.forms.bazaar.run import RunForm
from habit_tracker.models import BazaarRun


class RunFilter(django_filters.FilterSet):
    class Meta:
        model = BazaarRun
        fields = ['character', 'archetype', 'result']


class RunListView(PermissionRequiredMixin, FilterView):
    model = BazaarRun
    template_name = "habit_tracker/bazaar/bazaar.html"
    context_object_name = 'runs'
    filterset_class = RunFilter
    permission_required = 'habit_tracker.bazaar_access'
    ordering = ['-created_at']

class RunCreateView(PermissionRequiredMixin, CreateView):
    model = BazaarRun
    form_class = RunForm
    template_name = 'habit_tracker/bazaar/bazaar_form.html'
    success_url = reverse_lazy('habit_tracker:bazaar')
    permission_required = 'habit_tracker.bazaar_access'


class RunUpdateView(PermissionRequiredMixin, UpdateView):
    model = BazaarRun
    form_class = RunForm
    template_name = 'habit_tracker/bazaar/bazaar_form.html'
    success_url = reverse_lazy('habit_tracker:bazaar')
    permission_required = 'habit_tracker.bazaar_access'


class RunDeleteView(PermissionRequiredMixin, DeleteView):
    model = BazaarRun
    template_name = 'habit_tracker/bazaar/bazaar_form_delete.html'
    success_url = reverse_lazy('habit_tracker:bazaar')
    permission_required = 'habit_tracker.bazaar_access'
