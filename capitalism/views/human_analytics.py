from django.shortcuts import render

from capitalism.services.human_analytics import HumanJobAnalyticsService


class HumanAnalyticsView:
    template_name = "capitalism/human_analytics.html"

    @staticmethod
    def home(request):
        stats = HumanJobAnalyticsService().run()
        context = {"stats": stats}
        return render(request, HumanAnalyticsView.template_name, context)
