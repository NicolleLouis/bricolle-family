from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from shopping_list.models.ingredient_history import IngredientHistory


class IngredientHistoryController:
    @staticmethod
    def index(request):
        histories = IngredientHistory.objects.select_related("ingredient")

        period = request.GET.get("period", "all")
        if period == "6m":
            since = timezone.now() - timezone.timedelta(days=180)
            histories = histories.filter(bought_date__gte=since)
        elif period == "1m":
            since = timezone.now() - timezone.timedelta(days=30)
            histories = histories.filter(bought_date__gte=since)

        items = (
            histories.values(
                "ingredient__name", "ingredient__unit", "ingredient__category"
            )
            .annotate(total_quantity=Sum("quantity"))
            .order_by("ingredient__name")
        )

        return render(
            request,
            "shopping_list/index_ingredient_history.html",
            {
                "items": items,
                "period": period,
            },
        )
