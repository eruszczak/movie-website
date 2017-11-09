from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag(name='get_pagination_query_string')
def get_pagination_query_string(get_request, page_kwarg='page'):
    """returns encoded query string parameters but without 'page' because it comes from 'page_obj'"""
    get_request = get_request.copy()
    try:
        get_request.pop(page_kwarg)
    except KeyError:
        pass
    encoded_query_string = urlencode(get_request)
    return '&{}'.format(encoded_query_string) if encoded_query_string else ''
