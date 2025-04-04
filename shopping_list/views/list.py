from django.contrib.auth.decorators import permission_required
from django.shortcuts import render


@permission_required('shopping_list.shopping_list_access', raise_exception=True)
def shopping_list(request):
    return render(request, "shopping_list/error.html", {"message": "Not Implemented"})
