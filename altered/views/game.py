from django.shortcuts import render, redirect

from altered.forms.new_game import GameForm


def game_form_view(request):
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('altered:game_form')
    else:
        form = GameForm()
    return render(request, 'altered/game_form.html', {'form': form})
