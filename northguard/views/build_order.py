from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect

from northguard.forms.build_order import BuildOrderForm
from northguard.forms.build_order_step import BuildOrderStepFormSet
from northguard.models import BuildOrder


class BuildOrderController:
    @staticmethod
    def index(request):
        build_orders = BuildOrder.objects.all()
        return render(
            request,
            "northguard/build_order_list.html",
            {"build_orders": build_orders}
        )

    @staticmethod
    def edit(request, build_order_id):
        build_order = get_object_or_404(BuildOrder, id=build_order_id)
        if request.method == 'POST':
            form = BuildOrderForm(request.POST, instance=build_order)
            formset = BuildOrderStepFormSet(request.POST, instance=build_order)
            if form.is_valid() and formset.is_valid():
                with transaction.atomic():
                    build_order = form.save()
                    build_order.steps.all().delete()
                    steps = formset.save(commit=False)

                    for index, step in enumerate(steps):
                        step.order = index
                        step.save()

                    formset.save_m2m()
                return redirect('northguard:build_order_index')
            else:
                return render(
                    request,
                    "northguard/error.html",
                    {"message": "There was an issue while saving this build_order"}
                )
        else:
            form = BuildOrderForm(instance=build_order)
            formset = BuildOrderStepFormSet(instance=build_order)

        return render(request, 'northguard/build_order_edit.html', {
            'form': form,
            'formset': formset,
            'build_order': build_order,
        })
