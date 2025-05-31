from django.shortcuts import render, redirect
from altered.forms import GameForm

def game_form_view(request):
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('game_form')  # Redirect to the same page
    else:
        form = GameForm()
    return render(request, 'altered/game_form.html', {'form': form})
