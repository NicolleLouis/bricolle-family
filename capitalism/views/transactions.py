from django.shortcuts import render

from capitalism.services import TransactionListingService


class TransactionsView:
    template_name = "capitalism/transactions.html"

    @staticmethod
    def home(request):
        object_type = request.GET.get("object_type")
        context = TransactionListingService(object_type=object_type).run()
        return render(request, TransactionsView.template_name, context)
