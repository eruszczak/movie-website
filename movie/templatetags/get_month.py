from django import template

register = template.Library()


@register.filter
def get_month(value):
    month = value[5:7]
    if month[0] == '0':
        return month[1]
    return month
