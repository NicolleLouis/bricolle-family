from django.shortcuts import render

from capitalism.services.object_statistics import ObjectInventoryStatisticsService


class ObjectsView:
    template_name = "capitalism/objects.html"

    @staticmethod
    def home(request):
        stats = ObjectInventoryStatisticsService().run()
        context = {"stats": stats}
        return render(request, ObjectsView.template_name, context)
