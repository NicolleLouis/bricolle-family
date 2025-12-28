from django.shortcuts import render

from capitalism.constants.object_type import ObjectType
from capitalism.models import PriceAnalytics
from capitalism.services.pricing import PriceAnalyticsChartsService


class PriceAnalyticsView:
    template_name = "capitalism/price_analytics.html"

    @staticmethod
    def home(request):
        object_type = request.GET.get("object", ObjectType.WOOD)
        choices = dict(ObjectType.choices)

        if object_type not in choices:
            object_type = ObjectType.WOOD

        analytics = (
            PriceAnalytics.objects.filter(object_type=object_type)
            .order_by("day_number")
        )

        average_price_chart, transaction_chart = PriceAnalyticsChartsService().render(
            object_type=object_type
        )

        context = {
            "object_choices": ObjectType.choices,
            "selected_object": object_type,
            "analytics": analytics,
            "object_label": choices.get(object_type, object_type),
            "average_price_chart": average_price_chart,
            "transaction_chart": transaction_chart,
        }

        return render(request, PriceAnalyticsView.template_name, context)
