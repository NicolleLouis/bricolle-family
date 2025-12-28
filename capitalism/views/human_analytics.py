from django.shortcuts import render

from capitalism.constants.jobs import Job
from capitalism.models import HumanAnalytics
from capitalism.services.human_analytics import (
    AverageMoneyChartService,
    HumanJobAnalyticsService,
    HumanNeedsSatisfactionChartService,
)


class HumanRepartitionView:
    template_name = "capitalism/human_repartition.html"

    @staticmethod
    def home(request):
        stats = HumanJobAnalyticsService().run()
        needs_chart = HumanNeedsSatisfactionChartService().render()
        context = {"stats": stats, "needs_chart": needs_chart}
        return render(request, HumanRepartitionView.template_name, context)


class HumanAnalyticsView:
    template_name = "capitalism/human_analytics.html"

    @staticmethod
    def home(request):
        job = request.GET.get("job", Job.MINER)
        job_labels = dict(Job.choices)

        if job not in job_labels:
            job = Job.MINER

        analytics = (
            HumanAnalytics.objects.filter(job=job)
            .order_by("day_number")
        )

        average_money_chart = AverageMoneyChartService().render(job=job)

        context = {
            "job_choices": Job.choices,
            "selected_job": job,
            "job_label": job_labels.get(job, job),
            "analytics": analytics,
            "average_money_chart": average_money_chart,
        }
        return render(request, HumanAnalyticsView.template_name, context)
