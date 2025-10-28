from decimal import Decimal

from django.db.models import Sum, F, DecimalField, ExpressionWrapper, OuterRef, Subquery, Value, Q
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from altered.models import UniqueFlip, UniquePrice
from altered.forms import (
    UniqueFlipPurchaseForm,
    UniqueFlipSellForm,
    UniqueFlipFilterForm,
    UniqueFlipCurrentPriceForm,
)

BALANCE_EXPRESSION = ExpressionWrapper(
    (Coalesce(F('sold_price'), 0) * Decimal('0.95')) - F('bought_price'),
    output_field=DecimalField(max_digits=10, decimal_places=2),
)

# Include historic sales completed before the marketplace tracking existed.
PRE_MARKETPLACE_BALANCE = Decimal('400')


def unique_flip_list_view(request):
    status = request.GET.get('status', 'current')
    sort = request.GET.get('sort')
    filter_form = UniqueFlipFilterForm(request.GET)
    faction = None
    hide_zero = False
    price_issues_only = False
    if filter_form.is_valid():
        faction = filter_form.cleaned_data.get('faction') or None
        hide_zero = filter_form.cleaned_data.get('hide_zero')
        price_issues_only = filter_form.cleaned_data.get('price_issues_only')

    purchase_form = UniqueFlipPurchaseForm()

    if request.method == 'POST':
        response, purchase_form = _handle_post(request, status, purchase_form)
        if response:
            return response

    flips = _filter_flips(
        UniqueFlip.objects.all(),
        status,
        faction,
        hide_zero,
        price_issues_only,
    )
    flips = _sort_flips(flips, sort)
    flips = flips.annotate(balance_value=BALANCE_EXPRESSION)

    metrics = _compute_metrics(hide_zero)

    context = {
        'flips': flips,
        'status': status,
        'selected_faction': faction,
        **metrics,
        'hide_zero': hide_zero,
        'price_issues_only': price_issues_only,
        'sort': sort,
        'purchase_form': purchase_form,
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


def _handle_post(request, status, purchase_form):
    if 'purchase' in request.POST:
        form = UniqueFlipPurchaseForm(request.POST)
        if form.is_valid():
            UniqueFlip.objects.create(
                unique_id=form.cleaned_data['unique_id'],
                bought_price=form.cleaned_data['bought_price'],
                bought_at=timezone.now(),
            )
            return redirect('altered:unique_flip_list'), purchase_form
        return None, form

    if 'sell' in request.POST:
        flip = get_object_or_404(UniqueFlip, id=request.POST.get('flip_id'))
        form = UniqueFlipSellForm(request.POST)
        if form.is_valid():
            flip.sold_price = form.cleaned_data['sold_price']
            flip.sold_at = timezone.now()
            flip.save()
            return redirect(request.path + f'?status={status}'), purchase_form

    if 'toggle_in_use' in request.POST:
        flip = get_object_or_404(UniqueFlip, id=request.POST.get('flip_id'))
        flip.in_use = not flip.in_use
        flip.save(update_fields=['in_use'])
        return redirect(request.path + f'?status={status}'), purchase_form

    if 'set_current_price' in request.POST:
        flip = get_object_or_404(UniqueFlip, id=request.POST.get('flip_id'))
        form = UniqueFlipCurrentPriceForm(request.POST)
        if form.is_valid():
            flip.save_price(form.cleaned_data['current_price'])
            return redirect(request.path + f'?status={status}'), purchase_form

    return None, purchase_form


def _filter_flips(queryset, status, faction, hide_zero, price_issues_only):
    if status == 'sold':
        queryset = queryset.filter(sold_at__isnull=False)
    else:
        queryset = queryset.filter(sold_at__isnull=True)

    if faction:
        queryset = queryset.filter(faction=faction)

    if hide_zero:
        queryset = queryset.exclude(bought_price=0)

    if price_issues_only:
        latest_price_subquery = UniquePrice.objects.filter(
            unique_flip=OuterRef('pk')
        ).order_by('-date').values('price')[:1]
        queryset = queryset.annotate(latest_price=Subquery(latest_price_subquery))
        queryset = queryset.filter(
            Q(latest_price__isnull=True) |
            (Q(advised_price__isnull=False) & ~Q(advised_price=F('latest_price')))
        )

    return queryset


def _sort_flips(queryset, sort):
    if sort in ('bought_price', '-bought_price'):
        return queryset.order_by(sort)

    if sort in ('balance', '-balance'):
        order_field = ('-' if sort.startswith('-') else '') + 'balance_value'
        return queryset.annotate(balance_value=BALANCE_EXPRESSION).order_by(order_field)

    return queryset.order_by('-bought_at')


def _compute_metrics(hide_zero):
    balance_queryset = UniqueFlip.objects.filter(in_use=False)
    if hide_zero:
        balance_queryset = balance_queryset.exclude(bought_price=0)
    balance = balance_queryset.aggregate(
        balance=Sum(BALANCE_EXPRESSION)
    )['balance'] or Decimal('0')
    balance += PRE_MARKETPLACE_BALANCE
    balance = round(balance, 2)

    sold_balance_queryset = UniqueFlip.objects.filter(sold_at__isnull=False)
    if hide_zero:
        sold_balance_queryset = sold_balance_queryset.exclude(bought_price=0)
    balance_sold_only = sold_balance_queryset.aggregate(
        balance=Sum(BALANCE_EXPRESSION)
    )['balance'] or Decimal('0')
    balance_sold_only = round(balance_sold_only, 2)

    stock_queryset = UniqueFlip.objects.filter(sold_at__isnull=True)
    if hide_zero:
        stock_queryset = stock_queryset.exclude(bought_price=0)
    stock_immobilised = stock_queryset.aggregate(total=Sum('bought_price'))['total'] or Decimal('0')
    stock_immobilised = round(stock_immobilised, 2)

    latest_price_subquery = UniquePrice.objects.filter(
        unique_flip=OuterRef('pk')
    ).order_by('-date').values('price')[:1]
    expected_gain_queryset = stock_queryset.annotate(
        latest_price=Subquery(latest_price_subquery)
    )
    expected_gain = expected_gain_queryset.aggregate(
        total=Sum(
            ExpressionWrapper(
                Coalesce(F('latest_price'), Value(Decimal('0'))) - F('bought_price'),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )
    )['total'] or Decimal('0')
    expected_gain = round(expected_gain, 2)

    return {
        'balance': balance,
        'balance_sold_only': balance_sold_only,
        'stock_immobilised': stock_immobilised,
        'expected_gain': expected_gain,
    }
