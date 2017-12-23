from csv import DictReader, DictWriter
from os import remove
from os.path import join

from django.core.exceptions import ValidationError

from importer.helpers import recognize_file_source, convert_to_datetime, fill_dictwriter_with_rating_qs, get_imdb_rss, \
    unpack_from_rss_item
from lists.models import Watchlist
from titles.constants import MY_HEADERS
from titles.models import Rating
from titles.tmdb_api import TmdbWrapper


def import_ratings_from_csv(user, file_path):
    """import missing ratings from csv file (exported from here or imdb)"""
    # file = file.read().decode('utf-8')  TODO -- i must take into account that I have 2 different files
    # TODO what about error in FOR LOOP? headers doesnt mean its valid
    # what if rate is incorrect (because if title or date is wrong is ok)
    with open(file_path, 'r') as f:
        mapper = recognize_file_source(f)
        print(mapper)
        if mapper:
            reader = DictReader(f)
            row_count, created_count = 0, 0
            for row in reader:
                row_count += 1
                imdb_id, rate_date, rate = row[mapper['imdb_id']], row[mapper['rate_date']], row[mapper['rate']]
                rate_date = convert_to_datetime(row[mapper['rate_date']], 'csv')
                title = TmdbWrapper().get(imdb_id=imdb_id)
                print('\n------------', imdb_id, rate_date, rate, title)
                if title and rate_date:
                    try:
                        r, created = Rating.objects.get_or_create(
                            user=user, title=title, rate_date=rate_date, defaults={'rate': rate}
                        )
                    except ValidationError as e:
                        print('. '.join(e.messages))
                    else:
                        if created:
                            print('creating', r)
                            created_count += 1
                        else:
                            print('existed', r)
                print('\n----------')
            print(f'imported {created_count} out of {row_count} ratings - {round((created_count / row_count) * 100, 2)}%')
        else:
            print('headers are wrong')
    remove(file_path)


def export_ratings(user):
    """
    exports to a csv file all of user's ratings, so they can be imported later
    file consists of lines in format: tt1234567,2017-05-23,7
    The file can be used to import ratings back using ImportRatingsView
    """
    user_tmp_folder = user.get_temp_folder_path(absolute=True, create=True)

    ratings = Rating.objects.filter(user=user).select_related('title')
    # count_ratings = ratings.count()
    # count_titles = ratings.values_list('title').distinct().count()
    # filename = '{}_ratings_for_{}_titles_{}'.format(count_ratings, count_titles, now().strftime('%Y-%m-%d'))
    filename = 'export'
    file_path = join(user_tmp_folder, f'{filename}.csv')
    with open(file_path, 'w') as csvfile:
        writer = DictWriter(csvfile, fieldnames=MY_HEADERS, lineterminator='\n')
        writer.writeheader()
        fill_dictwriter_with_rating_qs(writer, ratings)


def update_user_watchlist(user):
    """
    updates user's watchlist rss.imdb.com/user/<userid>/watchlist
    """
    itemlist = get_imdb_rss()
    if itemlist:
        updated_titles = []
        current_watchlist = []
        count = 0
        user_watchlist = Watchlist.objects.filter(user=user)
        print('update_user_watchlist', user)
        for obj in itemlist:
            const, date = unpack_from_rss_item(obj, for_watchlist=True)
            title = None
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


def update_user_ratings(user):
    """
    updates user's ratings using rss.imdb.com/user/<userid>/ratings
    """
    itemlist = get_imdb_rss()
    if itemlist:
        updated_titles = []
        count = 0
        print('update_user_ratings:', user)
        for i, item in enumerate(itemlist):
            const, rate_date, rate = unpack_from_rss_item(item)
            title = None
            if title and rate and rate_date:
                obj, created = Rating.objects.get_or_create(user=user, title=title, rate_date=rate_date,
                                                            defaults={'rate': rate})
                if created:
                    count += 1
                    if len(updated_titles) < 10:
                        updated_titles.append(title)
        return updated_titles, count
    return None
