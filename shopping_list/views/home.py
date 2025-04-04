from django.contrib.auth.decorators import permission_required
from django.shortcuts import render


@permission_required('shopping_list.shopping_list_access', raise_exception=True)
def home(request):
    return render(request, "shopping_list/home.html")
