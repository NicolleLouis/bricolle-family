from django.shortcuts import render, redirect


def configuration(request):
    return render(request, 'shopping_list/configuration.html')
