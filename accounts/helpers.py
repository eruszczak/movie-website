from csv import DictReader, DictWriter
from os.path import join

from django.core.exceptions import ValidationError
from django.utils.timezone import now

from titles.constants import MY_HEADERS, IMDB_HEADERS, IMDB_CSV_MAPPER, MY_CSV_MAPPER
from titles.helpers import fill_dictwriter_with_rating_qs
from common.prepareDB_utils import convert_to_datetime, valid_csv_header, get_csv_headers
from titles.models import Title, Rating
from titles.tmdb_api import TmdbWrapper


def recognize_file_source(f):
    headers = get_csv_headers(f)
    print(headers)
    if valid_csv_header(headers, MY_HEADERS):
        return MY_CSV_MAPPER
    elif valid_csv_header(headers, IMDB_HEADERS):
        return IMDB_CSV_MAPPER
    return None


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
                        print(''.join(e.messages))
                    else:
                        if created:
                            print('creating', r)
                            created_count += 1
                        else:
                            print('existed', r)
                print('\n----------')
            print(f'imported {created_count} out of {row_count} ratings - {round((created_count / row_count) * 100, 2)}%')

    # delete file


def export_ratings(user):
    """
    exports to a csv file all of user's ratings, so they can be imported later
    file consists of lines in format: tt1234567,2017-05-23,7
    """
    user_tmp_folder = user.get_temp_folder_path(absolute=True, create=True)

    ratings = Rating.objects.filter(user=user).select_related('title')
    count_ratings = ratings.count()
    count_titles = ratings.values_list('title').distinct().count()

    # filename = '{}_ratings_for_{}_titles_{}'.format(count_ratings, count_titles, now().strftime('%Y-%m-%d'))
    filename = 'export'
    file_path = join(user_tmp_folder, f'{filename}.csv')
    with open(file_path, 'w') as csvfile:
        writer = DictWriter(csvfile, fieldnames=MY_HEADERS, lineterminator='\n')
        writer.writeheader()
        fill_dictwriter_with_rating_qs(writer, ratings)
    return file_path
