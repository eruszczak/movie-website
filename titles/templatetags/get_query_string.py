from django import template
from urllib.parse import urlencode, parse_qsl

register = template.Library()


@register.simple_tag(name='get_query_string')
def get_query_string(get_request, *args):
    """
        returns encoded query string without page parameter and extra parameter names passed as *args
        Using parse_qsl because I need a list and get_request.urlencode() because it gives an access to multiple values
        eg. genre=2&genre=8
    """
    get_request = get_request.copy()
    parameters_to_exclude = ['page']
    parameters_to_exclude.extend(list(args))
    for parameter in parameters_to_exclude:
        try:
            get_request.pop(parameter)
        except KeyError:
            pass

    parameter_list = parse_qsl(get_request.urlencode())
    encoded_query_string = urlencode(parameter_list)
    return '&{}'.format(encoded_query_string) if encoded_query_string else ''
