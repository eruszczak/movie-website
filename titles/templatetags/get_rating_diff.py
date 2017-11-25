from django import template
from django.utils.timezone import now

register = template.Library()


@register.simple_tag(name='get_rating_diff')
def get_rating_diff(ratings, index):
    date = ratings[index].rate_date
    if index == 0:
        date_delta = now().date() - date
    else:
        date_delta = ratings[index - 1].rate_date - date

    if index == len(ratings) - 1:
        rate_delta = 0
    else:
        rate_delta = ratings[index].rate - ratings[index + 1].rate

    return {
        'rate': rate_delta,
        'date': date_delta.days
    }
