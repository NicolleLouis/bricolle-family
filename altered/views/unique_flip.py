from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from altered.models import UniqueFlip
from altered.forms import UniqueFlipPurchaseForm, UniqueFlipSellForm


def unique_flip_list_view(request):
    status = request.GET.get('status', 'current')

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
    else:
        form = UniqueFlipPurchaseForm()

    flips = UniqueFlip.objects.order_by('-bought_at')
    if status == 'sold':
        flips = flips.filter(sold_at__isnull=False)
    else:
        flips = flips.filter(sold_at__isnull=True)

    balance = UniqueFlip.objects.aggregate(
        balance=Sum(
            ExpressionWrapper(
                F('sold_price') - F('bought_price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
    )['balance'] or 0

    context = {
        'flips': flips,
        'status': status,
        'balance': balance,
        'purchase_form': form,
        'sell_form': UniqueFlipSellForm(),
    }
    return render(request, 'altered/unique_flip_list.html', context)
