from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib.parse import urlencode
import datetime


def build_url(url, **kwargs):
    get = kwargs.pop('get', {})
    url += '?' + urlencode(get)
    return url


def build_datetime_obj(obj):
    if isinstance(obj, datetime.date):
        return datetime.datetime(obj.year, obj.month, obj.day)
    return None


def paginate(query_set, page, page_size=50):
    paginator = Paginator(query_set, page_size)
    try:
        ratings = paginator.page(page)
    except PageNotAnInteger:
        ratings = paginator.page(1)
    except EmptyPage:
        ratings = paginator.page(paginator.num_pages)
    return ratings
