from django.contrib import messages
from django.shortcuts import redirect, render

from slay_the_spire2.tasks import reparse_all_run_files


def settings(request):
    if request.method == "POST":
        reparse_all_run_files.delay()
        messages.success(request, "Le reparse de tous les fichiers run a ete lance en asynchrone.")
        return redirect("slay_the_spire2:settings")

    return render(request, "slay_the_spire2/settings.html")
