from django.shortcuts import render

from baby_name.forms.mass_yes import MassYesForm
from baby_name.services.mass_yes import MassYesService


class ScriptController:
    @staticmethod
    def glossary(request):
        return render(request, "baby_name/scripts_home.html")

    @staticmethod
    def mass_yes(request):
        form = MassYesForm(request.POST or None)
        mass_yes_result = None
        is_submitted = False

        if request.method == "POST":
            is_submitted = True
            if form.is_valid():
                service = MassYesService()
                mass_yes_result = service.execute(
                    raw_names=form.cleaned_data["names"],
                    family=form.cleaned_data["family"],
                    source_name=request.user.username,
                    sex=form.cleaned_data["sex"],
                )

        context = {
            "form": form,
            "mass_yes_result": mass_yes_result,
            "is_submitted": is_submitted,
        }
        return render(request, "baby_name/scripts_mass_yes.html", context)
