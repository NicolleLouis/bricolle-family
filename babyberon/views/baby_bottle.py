from django.shortcuts import render, redirect

from babyberon.forms.baby_bottle import BabyBottleForm


class BabyBottleController:
    @staticmethod
    def add_baby_bottle(request):
        if request.method == 'POST':
            form = BabyBottleForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('babyberon:home')
            else:
                return render(
                    request,
                    "babyberon/error.html",
                    {"message": "There was an issue while saving this baby bottle"}
                )
        else:
            form = BabyBottleForm()
        return render(request, 'babyberon/add_baby_bottle.html', {'form': form})
