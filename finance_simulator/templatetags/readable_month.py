from django import template

register = template.Library()


@register.filter(name='readable_month')
def readable_month(month_number):
    if not month_number:
        return f"0 ans"

    years = month_number / 12
    month_in_years = month_number % 12

    if month_in_years == 0:
        return f"{round(years)} année"
    return f"{month_in_years} mois"
