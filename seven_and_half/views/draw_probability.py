from django.shortcuts import render

from seven_and_half.forms.draw_probability import DrawProbabilityForm
from seven_and_half.services.draw_probability_service import DrawProbabilityService


def draw_probability(request):
    form = DrawProbabilityForm(request.POST or None)
    result = None
    bust_percentage = None
    success_percentage = None

    if request.method == "POST" and form.is_valid():
        service = DrawProbabilityService()
        result = service.calculate_draw_probabilities(form.cleaned_data["initial_card_value"])
        bust_percentage = round(result.bust_probability * 100, 2)
        success_percentage = round(result.success_probability * 100, 2)

    context = {
        "form": form,
        "result": result,
        "bust_percentage": bust_percentage,
        "success_percentage": success_percentage,
    }
    return render(request, "seven_and_half/draw_probability.html", context)
