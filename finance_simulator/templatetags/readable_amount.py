from django import template

register = template.Library()


@register.filter(name='readable_amount')
def readable_amount(amount):
    if not amount:
        return None

    return f"{int(amount):,}".replace(",", " ")
