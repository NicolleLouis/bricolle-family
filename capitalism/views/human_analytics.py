from django.shortcuts import render

from capitalism.constants.jobs import Job
from capitalism.models import HumanAnalytics
from capitalism.services.human_analytics import HumanJobAnalyticsService


class HumanRepartitionView:
    template_name = "capitalism/human_repartition.html"

    @staticmethod
    def home(request):
        stats = HumanJobAnalyticsService().run()
        context = {"stats": stats}
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

        context = {
            "job_choices": Job.choices,
            "selected_job": job,
            "job_label": job_labels.get(job, job),
            "analytics": analytics,
        }
        return render(request, HumanAnalyticsView.template_name, context)
