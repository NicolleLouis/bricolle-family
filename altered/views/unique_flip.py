from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from altered.models import UniqueFlip
from altered.forms import (
    UniqueFlipPurchaseForm,
    UniqueFlipSellForm,
    UniqueFlipFilterForm,
)


def unique_flip_list_view(request):
    status = request.GET.get('status', 'current')
    sort = request.GET.get('sort')
    filter_form = UniqueFlipFilterForm(request.GET)
    faction = None
    hide_zero = False
    if filter_form.is_valid():
        faction = filter_form.cleaned_data.get('faction') or None
        hide_zero = filter_form.cleaned_data.get('hide_zero')

    if request.method == 'POST':
        if 'purchase' in request.POST:
            form = UniqueFlipPurchaseForm(request.POST)
            if form.is_valid():
                UniqueFlip.objects.create(
                    unique_id=form.cleaned_data['unique_id'],
                    bought_price=form.cleaned_data['bought_price'],
                    bought_at=timezone.now(),
                )
                return redirect('altered:unique_flip_list')
        elif 'sell' in request.POST:
            flip = get_object_or_404(UniqueFlip, id=request.POST.get('flip_id'))
            form = UniqueFlipSellForm(request.POST)
            if form.is_valid():
                flip.sold_price = form.cleaned_data['sold_price']
                flip.sold_at = timezone.now()
                flip.save()
                return redirect(request.path + f'?status={status}')
        elif 'toggle_in_use' in request.POST:
            flip = get_object_or_404(UniqueFlip, id=request.POST.get('flip_id'))
            flip.in_use = not flip.in_use
            flip.save(update_fields=['in_use'])
            return redirect(request.path + f'?status={status}')
    else:
        form = UniqueFlipPurchaseForm()

    flips = UniqueFlip.objects.all()
    if status == 'sold':
        flips = flips.filter(sold_at__isnull=False)
    else:
        flips = flips.filter(sold_at__isnull=True)
    if faction:
        flips = flips.filter(faction=faction)
    if hide_zero:
        flips = flips.exclude(bought_price=0)

    balance_expression = ExpressionWrapper(
        Coalesce(F('sold_price'), 0) - F('bought_price'),
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )

    if sort in ('bought_price', '-bought_price'):
        flips = flips.order_by(sort)
    elif sort in ('balance', '-balance'):
        order_field = ('-' if sort.startswith('-') else '') + 'balance_value'
        flips = flips.annotate(balance_value=balance_expression).order_by(order_field)
    else:
        flips = flips.order_by('-bought_at')

    flips = flips.annotate(balance_value=balance_expression)

    balance_queryset = UniqueFlip.objects.filter(in_use=False)
    if hide_zero:
        balance_queryset = balance_queryset.exclude(bought_price=0)
    balance = balance_queryset.aggregate(
        balance=Sum(
            ExpressionWrapper(
                Coalesce(F('sold_price'), 0) - F('bought_price'),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )
    )['balance'] or 0

    context = {
        'flips': flips,
        'status': status,
        'selected_faction': faction,
        'balance': balance,
        'hide_zero': hide_zero,
        'sort': sort,
        'purchase_form': form,
        'sell_form': UniqueFlipSellForm(),
        'filter_form': filter_form,
    }
    return render(request, 'altered/unique_flip_list.html', context)


def unique_flip_detail_view(request, flip_id: int):
    flip = get_object_or_404(UniqueFlip, id=flip_id)
    if request.method == 'POST' and 'toggle_in_use' in request.POST:
        flip.in_use = not flip.in_use
        flip.save(update_fields=['in_use'])
        return redirect('altered:unique_flip_detail', flip_id=flip_id)
    return render(request, 'altered/unique_flip_detail.html', {'flip': flip})
