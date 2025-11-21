from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from flash_cards.forms import ThemePresetForm
from flash_cards.models import ThemePreset


def theme_presets(request, preset_id=None):
    presets = ThemePreset.objects.prefetch_related("categories").order_by("name")
    preset_instance = (
        get_object_or_404(ThemePreset, pk=preset_id) if preset_id else ThemePreset()
    )

    if request.method == "POST":
        form = ThemePresetForm(request.POST, instance=preset_instance)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Preset mis à jour." if preset_id else "Preset créé."
            )
            return redirect(reverse("flash_cards:theme_presets"))
    else:
        form = ThemePresetForm(instance=preset_instance)

    return render(
        request,
        "flash_cards/theme_presets.html",
        {
            "presets": presets,
            "form": form,
            "preset": preset_instance if preset_id else None,
        },
    )
