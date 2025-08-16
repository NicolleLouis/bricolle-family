import json

import django_filters
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, DeleteView
from django_filters.views import FilterView

from the_bazaar.constants.character import Character
from the_bazaar.forms.run import RunForm
from the_bazaar.forms.fight import FightForm
from the_bazaar.models import Run, Archetype, Fight
from django.db import models


class RunFilter(django_filters.FilterSet):
    class Meta:
        model = Run
        fields = ['character', 'archetype', 'result', 'greenheart_dungeon']


class RunListView(FilterView):
    model = Run
    template_name = "the_bazaar/run_list.html"
    context_object_name = 'runs'
    filterset_class = RunFilter
    ordering = ['-created_at']

FightFormSet = inlineformset_factory(Run, Fight, form=FightForm, extra=0, can_delete=True)

class RunCreateView(CreateView):
    model = Run
    form_class = RunForm
    template_name = 'the_bazaar/run_form.html'
    success_url = reverse_lazy('the_bazaar:run_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        character = form.data.get('character') or form.initial.get('character')
        queryset = Archetype.objects.filter(is_meta_viable=True)
        if character:
            queryset = queryset.filter(character=character)
        form.fields['archetype'].queryset = queryset
        return form

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['fight_formset'] = FightFormSet(self.request.POST, instance=Run())
        else:
            data['fight_formset'] = FightFormSet(instance=Run())
        data['archetypes_by_character'] = json.dumps({
            char: list(Archetype.objects.filter(character=char, is_meta_viable=True).values('id', 'name'))
            for char, _ in Character.choices
        })
        data['max_day_number'] = 0
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        fight_formset = context['fight_formset']
        if fight_formset.is_valid():
            self.object = form.save()
            fight_formset.instance = self.object
            fight_formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                self.get_context_data(form=form, fight_formset=fight_formset)
            )

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['fight_formset'].is_valid()
        return self.render_to_response(context)


class RunUpdateView(UpdateView):
    model = Run
    form_class = RunForm
    template_name = 'the_bazaar/run_form.html'
    success_url = reverse_lazy('the_bazaar:run_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        character = form.data.get('character') or form.instance.character
        form.fields['archetype'].queryset = Archetype.objects.filter(
            character=character, is_meta_viable=True
        )
        return form

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        queryset = Fight.objects.filter(run=self.object).order_by('day_number')
        if self.request.POST:
            data['fight_formset'] = FightFormSet(self.request.POST, instance=self.object, queryset=queryset)
        else:
            data['fight_formset'] = FightFormSet(instance=self.object, queryset=queryset)
        max_day = queryset.aggregate(models.Max('day_number'))['day_number__max'] or 0
        data['max_day_number'] = max_day
        data['archetypes_by_character'] = json.dumps({
            char: list(Archetype.objects.filter(character=char, is_meta_viable=True).values('id', 'name'))
            for char, _ in Character.choices
        })
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        fight_formset = context['fight_formset']
        if fight_formset.is_valid():
            self.object = form.save()
            fight_formset.instance = self.object
            fight_formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                self.get_context_data(form=form, fight_formset=fight_formset)
            )

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['fight_formset'].is_valid()
        return self.render_to_response(context)


class RunDeleteView(DeleteView):
    model = Run
    template_name = 'the_bazaar/run_form_delete.html'
    success_url = reverse_lazy('the_bazaar:run_list')
