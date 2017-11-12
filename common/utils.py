from urllib.parse import urlencode


def build_url(url, **kwargs):
    get = kwargs.pop('get', {})
    url += '?' + urlencode(get)
    return url


def build_html_string_for_titles(titles):
    return ', '.join(['<a href="{}">{}</a>'.format(obj.get_absolute_url(), obj.name) for obj in titles])


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
