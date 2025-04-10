import django_filters
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, DeleteView
from django_filters.views import FilterView

from habit_tracker.forms.bazaar_run import BazaarRunForm
from habit_tracker.models import BazaarRun


class BazaarRunFilter(django_filters.FilterSet):
    class Meta:
        model = BazaarRun
        fields = ['character', 'archetype', 'result']


class BazaarRunListView(PermissionRequiredMixin, FilterView):
    model = BazaarRun
    template_name = "habit_tracker/bazaar.html"
    context_object_name = 'runs'
    filterset_class = BazaarRunFilter
    permission_required = 'habit_tracker.bazaar_access'


class BazaarRunCreateView(PermissionRequiredMixin, CreateView):
    model = BazaarRun
    form_class = BazaarRunForm
    template_name = 'habit_tracker/bazaar_form.html'
    success_url = reverse_lazy('habit_tracker:bazaar')
    permission_required = 'habit_tracker.bazaar_access'


class BazaarRunUpdateView(PermissionRequiredMixin, UpdateView):
    model = BazaarRun
    form_class = BazaarRunForm
    template_name = 'habit_tracker/bazaar_form.html'
    success_url = reverse_lazy('habit_tracker:bazaar')
    permission_required = 'habit_tracker.bazaar_access'


class BazaarRunDeleteView(PermissionRequiredMixin, DeleteView):
    model = BazaarRun
    template_name = 'habit_tracker/bazaar_form_delete.html'
    success_url = reverse_lazy('habit_tracker:bazaar')
    permission_required = 'habit_tracker.bazaar_access'
