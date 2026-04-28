from django import template

register = template.Library()


@register.filter
def compact_price(value):
    if value is None:
        return "-"

    try:
        numeric_value = int(value)
    except (TypeError, ValueError):
        return value

    absolute_value = abs(numeric_value)
    suffixes = (
        (1_000_000_000, "B"),
        (1_000_000, "M"),
        (1_000, "k"),
    )

    for threshold, suffix in suffixes:
        if absolute_value >= threshold:
            compact_value = numeric_value / threshold
            if compact_value.is_integer():
                return f"{int(compact_value)}{suffix}"
            return f"{compact_value:.1f}{suffix}"

    return str(numeric_value)
