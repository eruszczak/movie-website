from django.utils import timezone

from common.prepareDB import update_user_ratings_csv, update_user_ratings, update_user_watchlist
from common.utils import build_html_string_for_titles


msgs = {
    'updated': 'Used {}. Updated {} titles: {}.',
    'updated_nothing': 'Updated nothing using {}',
    'watchlist_updated': '(rss watchlist) Updated {} titles: {}',
    'watchlist_deleted': '{}Deleted {} titles: {}',
    'error': 'Problem with fetching data. IMDb may be down, you provided wrong IMDb Id or your list is private.',
    'csv_error': 'Csv file seem incorrect (headers do not match) or file was not found.',
    'timeout': 'Wait a few minutes'
}


def update_ratings_using_csv(user):
    """
    wrapper for updating ratings using csv. check if update can be done and return message
    """
    if user.can_update_csv_ratings:
        user.last_updated_csv_ratings = timezone.now()
        user.save(update_fields=['last_updated_csv_ratings'])
        data = update_user_ratings_csv(user)
        if data is not None:
            updated_titles, count = data
            csv_filename = str(user.csv_ratings).split('/')[-1]
            if updated_titles:
                message = msgs['updated'].format(csv_filename, count, build_html_string_for_titles(updated_titles))
            else:
                message = msgs['updated_nothing'].format(csv_filename)
        else:
            message = msgs['csv_error']
    else:
        message = msgs['timeout']
    return message


def update_ratings(user):
    """
    wrapper for updating ratings using xml. check if update can be done and return message
    """
    if user.can_update_rss_ratings:
        user.last_updated_rss_ratings = timezone.now()
        user.save(update_fields=['last_updated_rss_ratings'])
        data = update_user_ratings(user)
        if data is not None:
            updated_titles, count = data
            link = '<a href="http://rss.imdb.com/user/{}/ratings">ratings</a>'.format(user.imdb_id)
            if updated_titles:
                message = msgs['updated'].format(link, count, build_html_string_for_titles(updated_titles))
            else:
                message = msgs['updated_nothing'].format(link)
        else:
            message = msgs['error']
    else:
        message = msgs['timeout']
    return message


def update_watchlist(user):
    """
    wrapper for updating watchlist using xml. check if update can be done and return message
    """
    if user.can_update_rss_watchlist:
        user.last_updated_rss_watchlist = timezone.now()
        user.save(update_fields=['last_updated_rss_watchlist'])
        data = update_user_watchlist(user)
        message = ''
        if data is not None:
            updated_titles, updated_titles_count = data['updated']
            deleted_titles, deleted_titles_count = data['deleted']
            link = '<a href="http://rss.imdb.com/user/{}/watchlist">watchlist</a>'.format(user.imdb_id)
            if updated_titles:
                message += msgs['updated'].format(link,
                                                  updated_titles_count,
                                                  build_html_string_for_titles(updated_titles))
            if deleted_titles:
                message += msgs['watchlist_deleted'].format('<br><br>' if message else '',
                                                            deleted_titles_count,
                                                            build_html_string_for_titles(deleted_titles))
            if not message:
                message = msgs['updated_nothing'].format(link)
        else:
            message = msgs['error']
    else:
        message = msgs['timeout']
    return message
