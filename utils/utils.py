from urllib.parse import urlencode


def build_url(url, **kwargs):
    get = kwargs.pop('get', {})
    if get:
        url += '?' + urlencode(get)
    return url
