import json

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect

from baby_name.constants.name_choice import NameChoice
from baby_name.forms.evaluation import EvaluationForm
from baby_name.models import Name, Evaluation


class EvaluationController:
    @staticmethod
    def get_or_update(request):
        if request.method == 'POST':
            form = EvaluationForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                score = form.cleaned_data['score']
                user = request.user

                evaluation, _created = Evaluation.objects.get_or_create(
                    name=name,
                    user=user,
                    defaults={'score': score}
                )

                evaluation.score = score
                evaluation.save()

                return redirect('baby_name:results')
            else:
                return render(
                    request,
                    "baby_name/error.html",
                    {"message": "Unknown Error"}
                )
        else:
            form = EvaluationForm()
        return render(request, 'baby_name/evaluation_form.html', {'form': form})

    @staticmethod
    def delete(request):
        try:
            data = json.loads(request.body)
            name_id = data.get('name_id')
            if not name_id:
                return JsonResponse({"status": "error", "message": "Missing name_id."}, status=400)

            name = get_object_or_404(Name, id=name_id)
            evaluation = Evaluation.objects.get(
                name=name,
                user=request.user,
            )
            evaluation.score = NameChoice.NON.value
            evaluation.save()

            return JsonResponse({"status": "success", "message": "Course removed."})

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")
