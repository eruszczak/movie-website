import datetime
from urllib.parse import urlencode

from django.core.mail import send_mail
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from mysite.settings import EMAIL_DEST, EMAIL_HOST_USER


def build_url(url, **kwargs):
    get = kwargs.pop('get', {})
    url += '?' + urlencode(get)
    return url


def send_email(subject, message):
    send_mail(
        subject,
        message,
        EMAIL_HOST_USER,
        [EMAIL_DEST],
        fail_silently=False,
        html_message=message,
    )


def build_html_string_for_titles(titles):
    return ', '.join(['<a href="{}">{}</a>'.format(obj.get_absolute_url(), obj.name) for obj in titles])


def paginate(query_set, page, page_size=50):
    paginator = Paginator(query_set, page_size)
    try:
        paginated_qs = paginator.page(page)
    except PageNotAnInteger:
        paginated_qs = paginator.page(1)
    except EmptyPage:
        paginated_qs = paginator.page(paginator.num_pages)
    return paginated_qs

# def email_watchlist():
#     from movie.models import ImdbWatchlist
#     delete = ImdbWatchlist.objects.to_delete()
#     message = """
#                 <table class="table table-hover table-bordered table-condensed">
#                 <thead>
#                     <tr>
#                         <th class="text-center">title</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#     """
#     message += '\n'.join(['<tr><td><a href="http://www.imdb.com/title/{1}/">{0}</a></td></tr>'.format(
#         obj.name, obj.const) for obj in delete])
#     message += '</tbody></table>'
#     print(message)
#     send_email(subject='[imdb watchlist]', message=message)
