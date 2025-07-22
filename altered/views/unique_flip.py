from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper

from altered.models import UniqueFlip


def unique_flip_list_view(request):
    status = request.GET.get('status', 'current')
    flips = UniqueFlip.objects.all().order_by('-bought_at')
    if status == 'sold':
        flips = flips.filter(sold_at__isnull=False)
    else:
        flips = flips.filter(sold_at__isnull=True)

    balance = UniqueFlip.objects.aggregate(
        balance=Sum(
            ExpressionWrapper(F('sold_price') - F('bought_price'),
                               output_field=DecimalField(max_digits=10, decimal_places=2))
        )
    )["balance"] or 0

    context = {
        'flips': flips,
        'status': status,
        'balance': balance,
    }
    return render(request, 'altered/unique_flip_list.html', context)
