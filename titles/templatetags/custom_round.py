from django import template

register = template.Library()


@register.filter
def custom_round(value):
    """Rounds a number to nearest 0.5"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    return round(value * 2.0) / 2.0
