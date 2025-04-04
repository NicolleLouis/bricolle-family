import json

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from baby_name.constants.name_choice import NameChoice
from baby_name.models import Name, Evaluation


def evaluation_delete(request):
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
