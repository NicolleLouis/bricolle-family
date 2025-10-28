from django.shortcuts import render

from capitalism.constants.object_type import ObjectType
from capitalism.models import PriceAnalytics


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

        context = {
            "object_choices": ObjectType.choices,
            "selected_object": object_type,
            "analytics": analytics,
            "object_label": choices.get(object_type, object_type),
        }

        return render(request, PriceAnalyticsView.template_name, context)
