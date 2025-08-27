from django import template
from django.utils import timezone

from agathe.constants.agathe import AgatheConstant

register = template.Library()

@register.filter
def feeding_color(last_datetime):
    if not last_datetime:
        return "#888888"

    now = timezone.now()
    elapsed_hours = max(0.0, (now - last_datetime).total_seconds() / 3600.0)

    t = elapsed_hours / AgatheConstant.FOOD_INTERVAL
    if t > 1.0:
        t = 1.0

    hue = 120.0 * (1.0 - t)

    return f"hsl({hue:.0f}, 85%, 45%)"
