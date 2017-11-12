import os
import csv

from django.conf import settings
from .prepareDB_utils import convert_to_datetime, get_rss, unpack_from_rss_item, add_new_title, valid_csv_headers
from titles.models import Title, Watchlist, Rating


def get_title_or_create(const):
    if not Title.objects.filter(const=const).exists():
        return add_new_title(const)
    return Title.objects.get(const=const)


def update_title(title):
    if title.can_be_updated:
        if add_new_title(title.const, update=True):
            message = 'Title updated successfully'
            return True, message
        else:
            message = 'Title wasn\'t updated'
    else:
        message = 'Too soon!'
    return False, message


def update_user_watchlist(user):
    """
    updates user's watchlist rss.imdb.com/user/<userid>/watchlist
    """
    itemlist = get_rss(user.userprofile.imdb_id, 'watchlist')
    if itemlist:
        updated_titles = []
        current_watchlist = []
        count = 0
        user_watchlist = Watchlist.objects.filter(user=user)
        print('update_user_watchlist', user)
        for obj in itemlist:
            const, date = unpack_from_rss_item(obj, for_watchlist=True)
            title = get_title_or_create(const)
            if title:
                current_watchlist.append(const)
                obj, created = Watchlist.objects.get_or_create(user=user, title=title,
                                                               defaults={'imdb': True, 'added_date': date})
                if created:
                    count += 1
                    if len(updated_titles) < 10:
                        updated_titles.append(title)
        no_longer_in_watchlist = user_watchlist.filter(imdb=True).exclude(title__const__in=current_watchlist)
        deleted_titles = [w.title for w in no_longer_in_watchlist]
        no_longer_in_watchlist.delete()
        return {
            'updated': (updated_titles, count),
            'deleted': (deleted_titles, len(deleted_titles))
        }
    return None


def update_user_ratings_csv(user):
    """
    updates user's ratings using ratings.csv exported from IMDb's list
    """
    path = os.path.join(settings.MEDIA_ROOT, str(user.userprofile.csv_ratings))
    if os.path.isfile(path):
        updated_titles = []
        count = 0
        print('update_user_ratings_csv:', user)
        with open(path, 'r') as f:
            if not valid_csv_headers(f):
                return None

            reader = csv.DictReader(f)
            for row in reader:
                title = get_title_or_create(row['const'])
                rate = row['You rated']
                rate_date = convert_to_datetime(row['created'], 'csv')
                if title and rate and rate_date:
                    obj, created = Rating.objects.get_or_create(user=user, title=title, rate_date=rate_date,
                                                                defaults={'rate': rate})
                    if created:
                        count += 1
                        if len(updated_titles) < 10:
                            updated_titles.append(title)
        return updated_titles, count
    return None


def update_user_ratings(user):
    """
    updates user's ratings using rss.imdb.com/user/<userid>/ratings
    """
    itemlist = get_rss(user.userprofile.imdb_id, 'ratings')
    if itemlist:
        updated_titles = []
        count = 0
        print('update_user_ratings:', user)
        for i, item in enumerate(itemlist):
            const, rate_date, rate = unpack_from_rss_item(item)
            title = get_title_or_create(const)
            if title and rate and rate_date:
                obj, created = Rating.objects.get_or_create(user=user, title=title, rate_date=rate_date,
                                                            defaults={'rate': rate})
                if created:
                    count += 1
                    if len(updated_titles) < 10:
                        updated_titles.append(title)
        return updated_titles, count
    return None
