from csv import DictReader, DictWriter
from os import remove
from os.path import join
from zipfile import ZipFile, ZIP_DEFLATED

from django.db.models import F
from django.utils.timezone import now

from importer.constants import EXPORT_FILE_NAME
from importer.helpers import recognize_file_source, convert_to_datetime, get_imdb_rss, unpack_from_rss_item
from lists.models import Watchlist
from titles.constants import MY_HEADERS
from titles.forms import RateForm
from titles.models import Rating
from tmdb.api import TmdbWrapper


def import_ratings_from_csv(user, file_path):
    """import missing ratings from csv file (exported from here or imdb)"""
    try:
        f = open(file_path, 'r', encoding='ISO-8859-1')
        mapper = recognize_file_source(f)
    except Exception as e:
        print(e)
    else:
        if mapper:
            reader = DictReader(f)
            row_count, created_count = 0, 0
            for row in reader:
                row_count += 1
                imdb_id, rate_date, rate = row[mapper['imdb_id']], row[mapper['rate_date']], row[mapper['rate']]
                rate_date = convert_to_datetime(row[mapper['rate_date']], 'csv')
                title = TmdbWrapper().get(imdb_id=imdb_id)
                if title and rate_date and not Rating.objects.filter(
                        user=user, title=title, rate_date=rate_date).exists():
                    data = {
                        'rate_date': rate_date,
                        'rate': rate
                    }
                    form = RateForm(user=user, title=title, data=data)
                    if form.is_valid():
                        created_count += 1
                        form.save()
                    else:
                        if form.errors:
                            for error in form.errors.items():
                                print(error)
                # else:
                #     print('existed or title or rate_date is missing')
            print(f'imported {created_count} out of {row_count} ratings '
                  f'- {round((created_count / row_count) * 100, 2)}%')
        else:
            print('headers are wrong')

        f.close()
    finally:
        remove(file_path)


def export_ratings(user):
    """
    exports to a csv file all of user's ratings, so they can be imported later
    file consists of lines in format: tt1234567,2017-05-23,7
    The file can be used to import ratings back using ImportRatingsView
    """
    user_tmp_folder = user.get_temp_folder_path(absolute=True, create=True)
    ratings = Rating.objects.filter(user=user).annotate(imdb_id=F('title__imdb_id')).select_related('title')
    temp_file_path = join(user_tmp_folder, 'temp.csv')
    with open(temp_file_path, 'w') as csvfile:
        writer = DictWriter(csvfile, fieldnames=MY_HEADERS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(ratings.values('imdb_id', 'rate', 'rate_date'))

    zip_file_path = join(user_tmp_folder, EXPORT_FILE_NAME)
    zf = ZipFile(zip_file_path, 'w')
    zf.write(temp_file_path, f"{now().strftime('%Y-%m-%d')}_ratings_{ratings.count()}.csv", ZIP_DEFLATED)
    zf.close()
    remove(temp_file_path)


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
