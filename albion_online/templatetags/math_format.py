from django import template

register = template.Library()


@register.filter
def format_percent(value):
    if value is None:
        return "-"

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return value

    if numeric_value.is_integer():
        formatted_value = str(int(numeric_value))
    else:
        formatted_value = f"{numeric_value:.1f}".rstrip("0").rstrip(".")

    if numeric_value > 0:
        return f"+{formatted_value}%"
    return f"{formatted_value}%"
