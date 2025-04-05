from django.shortcuts import render, redirect

from baby_name.forms.name import NameForm


def add_name(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            name = form.save()
            name.source = request.user.username
            name.save()
            return redirect('baby_name:vote_form')
        else:
            return render(
                request,
                "baby_name/error.html",
                {"message": "Name already present in database"}
            )
    else:
        form = NameForm()
    return render(request, 'baby_name/add_name.html', {'form': form})
