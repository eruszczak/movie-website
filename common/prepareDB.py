import os
import csv
import sys

from django.conf import settings
from .prepareDB_utils import convert_to_datetime, get_rss, unpack_from_rss_item, add_new_title
from django.contrib.auth.models import User
from movie.models import Title, Watchlist, Rating


def get_title_or_create(const):
    if not Title.objects.filter(const=const).exists():
        is_added = add_new_title(const)
        if not is_added:
            return False
    return Title.objects.get(const=const)


def update_title(const):
    return add_new_title(const, update=True)


def get_watchlist(user):
    itemlist = get_rss(user.userprofile.imdb_id, 'watchlist')
    if itemlist:
        updated_titles = []
        current_watchlist = []
        user_watchlist = Watchlist.objects.filter(user=user)
        print('get_watchlist', user)
        for obj in itemlist:
            const, name, date = unpack_from_rss_item(obj, for_watchlist=True)
            title = get_title_or_create(const)
            current_watchlist.append(const)
            obj, created = Watchlist.objects.get_or_create(user=user, title=title,
                                                           defaults={'imdb': True, 'added_date': date})
            if created:
                updated_titles.append(title)
        no_longer_in_watchlist = user_watchlist.filter(imdb=True).exclude(title__const__in=current_watchlist)
        deleted_titles = [w.title for w in no_longer_in_watchlist]
        no_longer_in_watchlist.delete()
        return updated_titles, deleted_titles
    return None, None


def update_from_csv(user):
    path = os.path.join(settings.MEDIA_ROOT, str(user.userprofile.csv_ratings))
    if os.path.isfile(path):
        updated_titles = []
        count = 0
        print('update_from_csv:', user)
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for num, row in enumerate(reader):
                title = get_title_or_create(row['const'])
                if title:
                    rate_date = convert_to_datetime(row['created'], 'csv')
                    obj, created = Rating.objects.get_or_create(user=user, title=title, rate_date=rate_date,
                                                                defaults={'rate': row['You rated']})
                    if created:
                        count += 1
                        if len(updated_titles) < 10:
                            updated_titles.append(title)
        return updated_titles, count
    return None, None


def update_from_rss(user):
    itemlist = get_rss(user.userprofile.imdb_id, 'ratings')
    if itemlist:
        updated_titles = []
        count = 0
        print('update_from_rss:', user)
        for i, item in enumerate(itemlist):
            const, rate, rate_date = unpack_from_rss_item(item)
            title = get_title_or_create(const)
            if title:
                obj, created = Rating.objects.get_or_create(user=user, title=title, rate_date=rate_date,
                                                            defaults={'rate': rate})
                if created:
                    count += 1
                    if len(updated_titles) < 10:
                        updated_titles.append(title)
        return updated_titles, count
    return None, None


def update_users_ratings_from_rss():
    for user in User.objects.filter(userprofile__imdb_id__isnull=False):
        update_from_rss(user)


def update_users_ratings_from_csv():
    for user in User.objects.exclude(userprofile__csv_ratings=''):
        update_from_csv(user)


def update_users_watchlist():
    for user in User.objects.filter(userprofile__imdb_id__isnull=False):
        get_watchlist(user)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        command = sys.argv[1]
        if command == 'allrss':
            update_users_ratings_from_rss()
        elif command == 'allcsv':
            update_users_ratings_from_csv()
        elif command == 'allwatchlist':
            update_users_watchlist()
